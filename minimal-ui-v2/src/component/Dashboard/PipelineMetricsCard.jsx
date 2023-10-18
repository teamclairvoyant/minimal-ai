import { Flex, Card, Statistic } from "antd"
import { Icon } from '@iconify/react';
import propTypes from "prop-types";


const pipelineMetricsBox = {
    boxShadow: "0px 0px 0px 0px",
    paddingTop: "1rem"
}
  
const pipelineMetricsCard = {
    boxShadow: "rgb(23 78 87) 0px 1px 2px 0px, rgb(248 248 248 / 53%) 0px 1px 6px -1px, rgb(8 8 8) 0px 2px 4px 0px",
    display: "flex",
    maxWidth: "20rem", 
    height:150,
    alignItems: "center",
    justifyContent: "center"
}
  
const innerCard = {
    display: "flex",
    alignItems: "center",
    width: "100%",
    justifyContent: "space-between"
}

PipelineMetricsCard.propTypes = {
    summary: propTypes.object
}

function PipelineMetricsCard({summary}) {
  return (
    <Flex gap="middle" style={pipelineMetricsBox} justify="space-between" align="center">
        <Card bordered={true} style={pipelineMetricsCard} bodyStyle={innerCard}>
            <Icon icon="cil:list" color="aqua" height={70} width={70} />
            <Statistic title="Pipelines" valueStyle={{color:"white"}} value={summary.total_pipelines}/>
        </Card>
        <Card bordered={true} style={pipelineMetricsCard} bodyStyle={innerCard}>
            <Icon icon="mdi:success-circle-outline" color="#77ed96" height={70} width={70} />
            <Statistic title="Successful Runs" style={{color:"white"}} value={summary.execution_details.COMPLETED}/>
        </Card>
        <Card bordered={true} style={pipelineMetricsCard} bodyStyle={innerCard}>
            <Icon icon="bx:run" color="yellow" height={70} width={70} />
            <Statistic title="Running" style={{color:"white"}} value={summary.execution_details.RUNNING}/>
        </Card>
        <Card bordered={true} style={pipelineMetricsCard} bodyStyle={innerCard}>
            <Icon icon="material-symbols:cancel-outline" color="orange" height={70} width={70} />
            <Statistic title="Cancelled" style={{color:"white"}} value={summary.execution_details.CANCELLED}/>
        </Card>
        <Card bordered={true} style={pipelineMetricsCard} bodyStyle={innerCard}>
            <Icon icon="ant-design:bug-filled" color="red" height={70} width={70} />
            <Statistic title="Failed" style={{color:"white"}} value={summary.execution_details.FAILED}/>
        </Card>
    </Flex>
  )
}

export default PipelineMetricsCard
