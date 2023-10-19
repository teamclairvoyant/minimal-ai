import { Card, Flex, Skeleton, Typography } from "antd";
import { useEffect, useState } from "react";
import { backendApi } from "../../api/api";
import PipelineMetricsCard from "../../component/Dashboard/PipelineMetricsCard";
import PipelineMetricsChart from "../../component/Dashboard/PipelineMetricsChart";

const { Title } = Typography

const subBarStyle = {
  width: '100%',
  color: "#fff"
}
const pipelineMetricsBox = {
  boxShadow: "rgb(23 78 87) 0px 1px 2px 0px, rgb(248 248 248 / 53%) 0px 1px 6px -1px, rgb(8 8 8) 0px 2px 4px 0px",
  marginLeft: "1rem",
  height: "17rem",
  width: "100%"
}

const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
]

const today = new Date()

function Dashboard() {
  const [summary, setSummary] = useState({"total_pipelines":0,"execution_details":{"COMPLETED":0,"FAILED":0,"CANCELLED":0,"RUNNING":0}})

  useEffect(() => {
    async function getSummary() {
      const response = await backendApi.get("/summary")
      if (response.data) {
        setSummary(response.data.summary)
      }
    }
    getSummary()
  }, [])

  if (!summary) return <Skeleton/>
  
  return (
    <Flex vertical>
      <Flex style={subBarStyle}>
        <Title level={3} style={{color:"white"}}>Today:&nbsp;&nbsp;{monthNames[today.getMonth()]}&nbsp;{today.getDate()},&nbsp;{today.getFullYear()}</Title>
      </Flex>
      
      <PipelineMetricsCard summary={summary} />
      
      <Flex style={{paddingTop: "1rem"}}>
        <PipelineMetricsChart completed={summary.execution_details.COMPLETED} failed={summary.execution_details.FAILED}
        cancelled={summary.execution_details.CANCELLED}/>
        <Card style={pipelineMetricsBox}><Skeleton></Skeleton></Card>
      </Flex>

    </Flex>
  )
}

export default Dashboard
