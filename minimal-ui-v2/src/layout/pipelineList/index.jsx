import { Typography, Space, Button, Input, Modal, Form } from 'antd'
import PipelineInfoTable from '../../component/PipelineList/PipelineInfoTable'
import { SearchOutlined } from '@ant-design/icons'
import { Icon } from '@iconify/react'
import { useState } from 'react'
import propTypes from "prop-types";
import { useNavigate } from 'react-router-dom';
import { backendApi } from '../../api/api'
import { pipelineStore } from '../../appState/pipelineStore'


const { Title } = Typography

const subBarStyle = {
    width: '100%',
    color: "#fff",
    display: 'flex',
    alignItems: 'center',
    paddingLeft: "24px",
    height: "40px"
}

NewPipelineForm.propTypes = {
  closeModal: propTypes.func
}

function NewPipelineForm({closeModal}) {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [, { setPipeline }] = pipelineStore()

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo)
  }

  async function createPipeline(values) {
    try{
      const response = await backendApi.post("/pipeline", {
        "name": values.name,
        "description": values.description
      })

      if (response.data.pipeline) {
        setPipeline(response.data.pipeline)
        navigate(`/pipeline/${response.data.pipeline.uuid}/edit`)
      }
    }
    catch(error) {
      console.log(error)
    }

  }

  return (
    <>
    <Form
    form={form}
      name="newPipeline"
      labelCol={{
        span: 8,
      }}
      wrapperCol={{
        span: 16,
      }}
      style={{
        maxWidth: 600,
      }}
      onFinish={createPipeline}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
    >
      <Form.Item
        label="Name"
        name="name"
        rules={[
          {
            required: true,
            message: 'Please enter pipeline name!',
          },
        ]}
      >
        <Input placeholder='pipeline name'/>
      </Form.Item>
  
      <Form.Item
        label="Description"
        name="description"
        rules={[
          {
            required: true,
            message: 'Please give short description of this pipeline',
          },
        ]}
      >
        <Input placeholder='description' />
      </Form.Item>
  
      <Form.Item

        wrapperCol={{
          offset: 8,
          span: 16
        }}

      >
        <Space direction='horizontal'>
          <Button onClick={() => {form.resetFields();closeModal(false)}}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </Space>
      </Form.Item>
    </Form>
    </>
  )
}

function PipelineList() {
  const [searchPipeline, setSearchPipeline] = useState("")
  const [open,setOpen] = useState(false)

  const showModal = () => {
    setOpen(true)
  }

  // const handleOk = () => {
  //   setConfirmLoading(true)
  //   setTimeout(() => {
  //     setOpen(false)
  //     setConfirmLoading(false)
  //   }, 2000)
  // }

  function search(e) {
    setSearchPipeline(e.target.value)
  }

  return (
    <div>
      <div style={subBarStyle}>
        <Title level={3} style={{color:"white"}}>All Pipelines</Title>
      </div>
      <Space direction='vertical' style={{width:"100%", paddingLeft:"24px", paddingTop:"10px"}}>
        <Space size={"large"}>
            <Button icon={<Icon icon={"ic:baseline-add"}/>} className='pipelineNew-btn-grad' onClick={showModal}>
                New Pipeline
            </Button>
            <Modal
              title="Create New Pipeline"
              open={open}
              onCancel={() => {setOpen(false)}}
              width={400}
              bodyStyle={{paddingTop:20}}
              footer={<></>}
            >
              <Space direction='vertical'>
                <NewPipelineForm closeModal={setOpen}/>
              </Space>
            </Modal>
            <Input placeholder='Search' prefix={<SearchOutlined/>} id={"pipeline-search"}
            onChange={(e) => {search(e)} } value={searchPipeline}/>
        </Space>
        <PipelineInfoTable searchItem={searchPipeline}/>
      </Space>
    </div>
  )
}

export default PipelineList
