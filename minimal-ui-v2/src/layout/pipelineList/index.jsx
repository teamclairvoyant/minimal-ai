import { SearchOutlined } from '@ant-design/icons'
import { Icon } from '@iconify/react'
import { Button, Flex, Form, Input, Modal, Space, Typography } from 'antd'
import propTypes from "prop-types"
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { backendApi } from '../../api/api'
import PipelineInfoTable from '../../component/PipelineList/PipelineInfoTable'

const { Title } = Typography

NewPipelineForm.propTypes = {
  closeModal: propTypes.func
}

function NewPipelineForm({closeModal}) {
  const [form] = Form.useForm()
  const navigate = useNavigate()

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo)
  }

  async function createPipeline(values) {
    try{

      const response = await backendApi.post("/pipeline", {
        "name": values.name,
        "description": values.description,
        "executor_type": "python"
      })

      if (response.data.pipeline) {
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
    <Flex vertical>

      <Title level={3} style={{color:"white"}}>All Pipelines</Title>

      <Flex gap={"large"} align='center'>
        <Button icon={<Icon icon={"ic:baseline-add"}/>} className='pipelineNew-btn-grad' onClick={showModal}>
          New Pipeline
        </Button>
        <Modal
          title="Create New Pipeline"
          open={open}
          onCancel={() => {setOpen(false)}}
          width={400}
          styles={{"body" : {paddingTop:20}}}
          footer={<></>}
        >
          <Flex vertical>
            <NewPipelineForm closeModal={setOpen}/>
          </Flex>
        </Modal>
        <Input placeholder='Search' prefix={<SearchOutlined/>} id={"pipeline-search"}
             onChange={(e) => {search(e)} } value={searchPipeline} style={{width:"12rem", height: "2.5rem"}}/>
      </Flex>

      <PipelineInfoTable searchItem={searchPipeline}/>      
    </Flex>
  )
}

export default PipelineList
