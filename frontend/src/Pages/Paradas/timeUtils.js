// timeUtils.js
export const formatDate = (dateStr) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
    return new Date(dateStr).toLocaleString('pt-BR', options);
  };
  
  export const checkAndFormatTimes = (startTime, endTime) => {
    const formattedStartTime = formatDate(startTime);
    const formattedEndTime = formatDate(endTime);
  
    // Verifica se as datas são diferentes
    if (startTime !== endTime) {
      return `${formattedStartTime} \n até \n${formattedEndTime}.`;
    } else {
      return `${formattedStartTime}.`;
    }
  };
  