import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import PropTypes from "prop-types";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Chart({ categoryBreakdown, totalBudget }) {
  const chartLabels = categoryBreakdown.map((item) => Object.keys(item)[0]);
  const chartData = categoryBreakdown.map((item) => Object.values(item)[0]);

  const generatedBlueColors = (count) => {
    const colors = [];
    for (let i = 0; i < count; i++) {
      const hue = 220;
      const saturation = 90;
      const lightness = 40 + i * (60 / count);
      colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
    }
    return colors;
  };

  const data = {
    labels: chartLabels,
    datasets: [
      {
        label: "비용 비중",
        data: chartData,
        backgroundColor: generatedBlueColors(chartData.length),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 22,
          padding: 20,
        },
      },
    },
  };

  return (
    <div className="w-64 mx-auto md:mx-0 flex flex-col items-center">
      <Doughnut data={data} options={options}/>
      <ul className="mt-4 text-sm text-center">
        {categoryBreakdown.map((item, idx) => {
          const label = Object.keys(item)[0];
          const value = Object.values(item)[0];
          return (
            <li key={idx}>
              {label}: ₩ {value.toLocaleString()}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

Chart.propTypes = {
  categoryBreakdown: PropTypes.array.isRequired,
  totalBudget: PropTypes.number.isRequired,
};