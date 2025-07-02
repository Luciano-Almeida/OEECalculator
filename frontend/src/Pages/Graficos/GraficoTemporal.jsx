import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer,
  ReferenceArea, Label 
} from 'recharts';
import {
  format, parseISO, set, addMinutes, isBefore, isEqual,
  setMinutes, setSeconds, setMilliseconds
} from 'date-fns';

const parseHourMinute = (timeStr) => {
  const [hour, minute] = timeStr.split(':').map(Number);
  return { hour, minute };
};

const gerarIntervalos = (start, end, stepMinutes) => {
  const result = [];
  let current = new Date(start);
  while (isBefore(current, end) || isEqual(current, end)) {
    result.push(new Date(current));
    current = addMinutes(current, stepMinutes);
  }
  return result;
};

const agruparEInterpolarDados = (discretizado, stepMinutes, startLimit, endLimit) => {
  const buckets = gerarIntervalos(startLimit, endLimit, stepMinutes);
  const bucketMap = new Map(buckets.map(b => [b.getTime(), { total_ok: 0, total_nok: 0 }]));

  discretizado.forEach(({ start, end, total_ok, total_nok }) => {
    const inicio = parseISO(start);
    const fim = parseISO(end);
    const duracaoTotalMs = fim - inicio;

    if (duracaoTotalMs <= 0) return; // ignora intervalos inválidos

    buckets.forEach((bucketStart) => {
      const bucketEnd = addMinutes(bucketStart, stepMinutes);

      const intersecaoInicio = inicio > bucketStart ? inicio : bucketStart;
      const intersecaoFim = fim < bucketEnd ? fim : bucketEnd;

      const duracaoIntersecaoMs = intersecaoFim - intersecaoInicio;

      if (duracaoIntersecaoMs > 0) {
        const proporcao = duracaoIntersecaoMs / duracaoTotalMs;
        const bucket = bucketMap.get(bucketStart.getTime());

        bucket.total_ok += total_ok * proporcao;
        bucket.total_nok += total_nok * proporcao;
      }
    });
  });

  return buckets.map((bucket, index) => {
    const valores = bucketMap.get(bucket.getTime()) || { total_ok: 0, total_nok: 0 };
    return {
      index,
      hora: format(bucket, 'HH:mm'),
      total_ok: Math.round(valores.total_ok),
      total_nok: Math.round(valores.total_nok),
      total_total: Math.round(valores.total_ok + valores.total_nok),
    };
  });
};

const GraficoTemporal = ({ discretizado, startTime = "08:00", endTime = "17:00", paradas = [] }) => {
  const start = parseHourMinute(startTime);
  const end = parseHourMinute(endTime);
  const now = new Date();

  const startLimit = set(now, {
    hours: start.hour,
    minutes: start.minute,
    seconds: 0,
    milliseconds: 0,
  });

  const endLimit = set(now, {
    hours: end.hour,
    minutes: end.minute,
    seconds: 0,
    milliseconds: 0,
  });

  // Define stepMinutes dinamicamente com base nos dados
  let stepMinutes = 15;
  if (discretizado.length > 1) {
    const d1 = parseISO(discretizado[0].start);
    const d2 = parseISO(discretizado[1].start);
    stepMinutes = Math.max(1, Math.round((d2 - d1) / 60000));
  }

  const data = agruparEInterpolarDados(discretizado, stepMinutes, startLimit, endLimit);

  const getIndexFromTime = (timeISO) => {
    const targetTime = parseISO(timeISO);
    let closestIndex = null;
    let closestDiff = Infinity;

    for (const d of data) {
      const [h, m] = d.hora.split(':').map(Number);
      const dataTime = set(now, { hours: h, minutes: m, seconds: 0, milliseconds: 0 });
      const diff = Math.abs(dataTime - targetTime);

      if (diff < closestDiff) {
        closestDiff = diff;
        closestIndex = d.index;
      }
    }

    return closestIndex;
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="index" tickFormatter={(idx) => data[idx]?.hora || ''} />
        <YAxis />
        <Tooltip
          formatter={(value, name) => [value, name === 'total_ok' ? 'Bons' : name === 'total_nok' ? 'Ruins' : name]}
          labelFormatter={(label) => {
            const item = data.find((d) => d.index === label);
            return item ? `Hora: ${item.hora}` : '';
          }}
        />
        <Legend />
        <Line type="monotone" dataKey="total_ok" stroke="#4CAF50" name="Bons" dot={false} />
        <Line type="monotone" dataKey="total_nok" stroke="#F44336" name="Ruins" dot={false} />
        {/* <Line type="monotone" dataKey="total_total" stroke="#2196F3" name="Total Geral" /> */}

        {paradas
          .filter((parada) => {
            const start = parseISO(parada.start_time);
            const end = parseISO(parada.end_time);
            return (
              isBefore(start, endLimit) &&
              isBefore(startLimit, end)
            );
          })
          .map((parada, idx) => {
            const x1 = getIndexFromTime(parada.start_time);
            const x2 = getIndexFromTime(parada.end_time);
            if (x1 === undefined || x2 === undefined || x1 === x2) return null;

            return (
              <ReferenceArea
                key={idx}
                x1={x1}
                x2={x2}
                strokeOpacity={0.3}
                fill="rgba(255, 193, 7, 0.3)"
              >
                <Label
                  value={parada.name}
                  position="insideTop"
                  fill="#0D47A1"
                  fontSize={12}
                  fontWeight="bold"
                  offset={10}
                />
              </ReferenceArea>
            );
          })}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default GraficoTemporal;
