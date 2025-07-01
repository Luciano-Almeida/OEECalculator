import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer,
  ReferenceArea, Label 
} from 'recharts';
import { format, parseISO, set, addMinutes, isBefore, isEqual } from 'date-fns';

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

const GraficoTemporal = ({ discretizado, startTime = "08:00", endTime = "17:00", paradas = [] }) => {
  const start = parseHourMinute(startTime);
  const end = parseHourMinute(endTime);

  // Cria uma base com data atual apenas pra montar a faixa horária
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

  // Descobre o step com base no primeiro intervalo do discretizado (ou usa 15 min por padrão)
  let stepMinutes = 15;
  if (discretizado.length > 1) {
    const d1 = parseISO(discretizado[0].start);
    const d2 = parseISO(discretizado[1].start);
    stepMinutes = Math.max(1, Math.round((d2 - d1) / 60000));
  }

  // Gera todos os horários entre startTime e endTime
  const intervalos = gerarIntervalos(startLimit, endLimit, stepMinutes);

  // Cria um mapa com os dados do discretizado
  const dataMap = new Map();
  discretizado.forEach((item) => {
    const hora = format(parseISO(item.start), 'HH:mm');
    dataMap.set(hora, {
      total_ok: item.total_ok ?? 0,
      total_nok: item.total_nok ?? 0,
    });
  });

  // Preenche os dados finais com todos os horários (mesmo os vazios)
  const data = intervalos.map((hora, index) => {
    const horaStr = format(hora, 'HH:mm');
    const valores = dataMap.get(horaStr) || { total_ok: 0, total_nok: 0 };
    return {
      index,
      hora: horaStr,
      total_ok: valores.total_ok,
      total_nok: valores.total_nok,
      total_total: valores.total_ok + valores.total_nok,
    };
  });

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
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="total_ok" stroke="#4CAF50" name="Bons" dot={false} />
        <Line type="monotone" dataKey="total_nok" stroke="#F44336" name="Ruins" dot={false} />
        {/*<Line type="monotone" dataKey="total_total" stroke="#2196F3" name="Total Geral" />*/}

        {/* Marcações de paradas */}
        {paradas
          .filter((parada) => {
            const start = parseISO(parada.start_time);
            const end = parseISO(parada.end_time);
            return (
              isBefore(start, endLimit) && // começa antes do fim do gráfico
              isBefore(startLimit, end)    // termina depois do início do gráfico
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
                  fill="#0D47A1"  // Azul escuro
                  fontSize={12}
                  fontWeight="bold"
                  offset={10}
                />
              </ReferenceArea>
            );
          })
        }

      </LineChart>
    </ResponsiveContainer>
  );
};

export default GraficoTemporal;
