import { Card, Empty } from "antd";
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js';
import propTypes from "prop-types";
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);


const pipelineMetricsCard = {
    boxShadow: "rgb(23 78 87) 0px 1px 2px 0px, rgb(248 248 248 / 53%) 0px 1px 6px -1px, rgb(8 8 8) 0px 2px 4px 0px",
    width: "30%",
    height: "17rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
}

PipelineMetricsChart.propTypes = {
  completed : propTypes.number,
  cancelled : propTypes.number,
  failed : propTypes.number
}

export default function PipelineMetricsChart({completed, cancelled, failed}) {
  if (completed == 0 & cancelled == 0 & failed == 0){
    return (
      <Card bordered={false} style={pipelineMetricsCard}>
        <Empty style={{paddingTop:30}}/>
      </Card>
    )
  }
  const data = {
    labels: ['Successful Runs', 'Failed', 'Cancelled'],
    datasets: [
      {
        label: '',
        data: [completed, cancelled, failed],
        backgroundColor: [
          'rgba(75, 192, 192, 0.2)',
          'rgba(255, 99, 132, 0.2)',
          'rgba(255, 159, 64, 0.2)',
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 1,
      },
    ],
    options: {
      responsive: false
    }
  }

  return (
    <Card bordered={false} style={pipelineMetricsCard} bodyStyle={{height:280,width:280}}>
        <Doughnut data={data} className='pipelineMetricsChart'/>
    </Card>
  )
}
