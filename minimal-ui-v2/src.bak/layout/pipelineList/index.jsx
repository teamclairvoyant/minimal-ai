import { Typography, Space, Button } from 'antd'
import PipelineInfoTable from '../../component/PipelineList/PipelineInfoTable'
import { Icon } from '@iconify/react';


const { Title } = Typography

const subBarStyle = {
    width: '100%',
    color: "#fff",
    display: 'flex',
    alignItems: 'center',
    paddingLeft: "24px",
    height: "40px"
}


function PipelineList() {
  return (
    <div>
      <div style={subBarStyle}>
        <Title level={3} style={{color:"white"}}>All Pipelines</Title>
      </div>
      <Space direction='vertical' style={{width:"100%", paddingLeft:"24px", paddingTop:"10px"}}>
        <Space>
            <Button type="primary" icon={<Icon icon={"ic:baseline-add"} />}>
                Download
            </Button>

        </Space>
        <PipelineInfoTable/>
      </Space>
    </div>
  )
}

export default PipelineList
