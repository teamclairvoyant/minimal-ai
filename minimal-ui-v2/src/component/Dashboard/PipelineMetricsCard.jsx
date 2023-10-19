import { Icon } from '@iconify/react';
import { Card, Flex, Statistic, Typography } from "antd";
import propTypes from "prop-types";

const pipelineMetricsBox = {
    boxShadow: "rgb(23 78 87) 0px 1px 2px 0px, rgb(248 248 248 / 53%) 0px 1px 6px -1px, rgb(8 8 8) 0px 2px 4px 0px",
    paddingTop: "1rem",
    marginTop: "1rem",
    backgroundColor: "rgb(21 20 20)"
}
  
const pipelineMetricsCard = {
    display: "flex",
    width: "20rem",
    alignItems: "center",
    justifyContent: "center",
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
    <Flex vertical gap="middle" style={pipelineMetricsBox}>
        <Typography.Title level={3} style={{margin:"0rem 2rem 0rem", }}>Run Metrics</Typography.Title>
        <Flex align='center' justify='space-between' style={{marginTop:"-1rem"}}>
            <Card bordered={false} style={pipelineMetricsCard} bodyStyle={innerCard}>
                <Icon icon="eos-icons:pipeline-outlined" color="aqua" height={70} width={70} />
                <Statistic title="Pipelines" valueStyle={{color:"white"}} value={summary.total_pipelines}/>
            </Card>
            <Card bordered={false} style={pipelineMetricsCard} bodyStyle={innerCard}>
                <Icon icon="mdi:success-circle-outline" color="#77ed96" height={70} width={70} />
                <Statistic title="Successful Runs" style={{color:"white"}} value={summary.execution_details.COMPLETED}/>
            </Card>
                <Card bordered={false} style={pipelineMetricsCard} bodyStyle={innerCard}>
                <Icon icon="bx:run" color="yellow" height={70} width={70} />
                <Statistic title="Running" style={{color:"white"}} value={summary.execution_details.RUNNING}/>
            </Card>
            <Card bordered={false} style={pipelineMetricsCard} bodyStyle={innerCard}>
                <Icon icon="material-symbols:cancel-outline" color="orange" height={70} width={70} />
                <Statistic title="Cancelled" style={{color:"white"}} value={summary.execution_details.CANCELLED}/>
            </Card>
            <Card bordered={false} style={pipelineMetricsCard} bodyStyle={innerCard}>
                <Icon icon="ant-design:bug-filled" color="red" height={70} width={70} />
                <Statistic title="Failed" style={{color:"white"}} value={summary.execution_details.FAILED}/>
            </Card>
        </Flex>
    </Flex>
  )
}

export default PipelineMetricsCard
