import { CloseOutlined, SettingOutlined } from "@ant-design/icons";
import { Icon } from "@iconify/react";
import {
  Button,
  Col,
  Drawer,
  Flex,
  Form,
  Input,
  Modal,
  Row,
  Space,
  Tooltip,
  Typography,
} from "antd";
import propTypes from "prop-types";
import { useEffect, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import { backendApi } from "../../../../minimal-ui/src/api/api";

import { pipelineStore } from "../../appState/pipelineStore";
import { taskStore } from "../../appState/taskStore";
import CustomNode from "./CustomNode";
import SinkNodeConfig from "./SinkNodeConfig";
import SorceNodeConfig from "./SourceNodeConfig";
import TransformNodeConfig from "./TransformNodeConfig";
//------------------------- Task Modal -------------------------
NewTaskForm.propTypes = {
  closeModal: propTypes.func,
  addNode: propTypes.func,
  nodeType: propTypes.string,
};

function NewTaskForm({ closeModal, addNode, nodeType }) {
  const [form] = Form.useForm();

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };

  async function createTask(values) {
    addNode(nodeType, values.name);
    form.resetFields();
    closeModal(false);
  }

  return (
    <Form
      form={form}
      name="newTask"
      labelCol={{
        span: 8,
      }}
      wrapperCol={{
        span: 16,
      }}
      style={{
        maxWidth: 600,
      }}
      onFinish={createTask}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
    >
      <Form.Item
        label="Name"
        name="name"
        rules={[
          {
            required: true,
            message: "Please enter task name!",
          },
        ]}
      >
        <Input placeholder="task" />
      </Form.Item>

      <Form.Item
        wrapperCol={{
          offset: 8,
          span: 16,
        }}
      >
        <Space direction="horizontal">
          <Button
            onClick={() => {
              form.resetFields();
              closeModal(false);
            }}
          >
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}

//------------------------- Sub header -------------------------
const SubHeader = ({
  pipeline,
  onExecute,
  onSave,
  onAdd,
  onRestore,
  flowInstance,
}) => {
  const [open, setOpen] = useState(false);
  const [nodeType, setNodeType] = useState("");

  const showModal = (type) => {
    setNodeType(type);
    setOpen(true);
  };

  return (
    <Flex
      style={{ height: "3rem", borderBottom: "solid black 1px", width: "100%" }}
      align="center"
    >
      <Col span={4}>
        <Button className="pipeline-name-div">{pipeline.name}</Button>
      </Col>

      <Col span={16}>
        <Flex align="center" style={{ width: "20rem" }} justify="space-between">
          <Button
            icon={<Icon icon={"material-symbols:add"} />}
            onClick={() => {
              showModal("data_loader");
            }}
          >
            source
          </Button>
          <Button
            icon={<Icon icon={"tabler:transform"} />}
            onClick={() => {
              showModal("data_transformer");
            }}
          >
            transform
          </Button>
          <Button
            icon={<Icon icon={"gg:database"} />}
            onClick={() => {
              showModal("data_sink");
            }}
          >
            sink
          </Button>
        </Flex>
      </Col>
      <Modal
        title="Create New Task"
        open={open}
        onCancel={() => {
          setOpen(false);
        }}
        width={400}
        styles={{ body: { paddingTop: 20 } }}
        footer={<></>}
      >
        <Flex vertical>
          <NewTaskForm
            closeModal={setOpen}
            addNode={onAdd}
            nodeType={nodeType}
            flowInstance={flowInstance}
          />
        </Flex>
      </Modal>

      <Col span={4}>
        <Row justify="end">
          <Col style={{ paddingRight: "1rem" }}>
            <Tooltip placement="bottom" title="restore">
              <Button
                ghost
                style={{ border: "solid gray 1px" }}
                icon={<Icon icon={"mdi:restore"} color="white" />}
                onClick={() => {
                  onRestore();
                }}
              />
            </Tooltip>
          </Col>
          <Col style={{ paddingRight: "1rem" }}>
            <Tooltip placement="bottom" title="save">
              <Button
                ghost
                style={{ border: "solid gray 1px" }}
                icon={
                  <Icon icon={"material-symbols:save-outline"} color="white" />
                }
                onClick={() => {
                  onSave();
                }}
              />
            </Tooltip>
          </Col>
          <Col style={{ paddingRight: "1rem" }}>
            <Tooltip placement="bottom" title="logs">
              <Button
                ghost
                style={{ border: "solid gray 1px" }}
                icon={
                  <Icon icon={"icon-park-outline:upload-logs"} color="white" />
                }
              />
            </Tooltip>
          </Col>
          <Tooltip placement="bottom" title="execute">
            <Button
              ghost
              style={{ border: "solid gray 1px" }}
              icon={<Icon icon={"solar:play-outline"} color="white" />}
              onClick={() => {
                onExecute();
              }}
            />
          </Tooltip>
        </Row>
      </Col>
    </Flex>
  );
};

SubHeader.propTypes = {
  pipeline: propTypes.object,
  onExecute: propTypes.func,
  onSave: propTypes.func,
  onAdd: propTypes.func,
  onRestore: propTypes.func,
  flowInstance: propTypes.object,
};

//---------------------------------Main workbook -------------------------

const nodeTypes = {
  draftNode: CustomNode,
  configuredNode: CustomNode,
  successNode: CustomNode,
  failNode: CustomNode,
};

const MainFlow = ({ pipeline, setPipeline }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rfInstance, setRfInstance] = useState(null);
  const { setViewport } = useReactFlow();
  const [currTask, setCurrTask] = useState(null);
  const [openTaskConfig, setOpenTaskConfig] = useState(false);
  const [, { setTask }] = taskStore();

  useEffect(() => {
    if (pipeline.reactflow_props) {
      const restoreFlow = async () => {
        const flow = pipeline.reactflow_props;

        if (Object.keys(flow).length != 0) {
          const { x = 0, y = 0, zoom = 1 } = flow.viewport;
          setNodes(flow.nodes || []);
          setEdges(flow.edges || []);
          setViewport({ x, y, zoom });
        }
      };

      restoreFlow();
    }
  }, [pipeline]);

  const onConnect = async (params) => {
    if (params) {
      let payload = {
        upstream_task_uuids: [params.source],
      };
      await backendApi.put(
        `/pipeline/${pipeline.uuid}/task/${params.target}`,
        payload
      );
    }

    setEdges((eds) => addEdge(params, eds));
  };

  const edgeOptions = {
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed },
  };

  const connectionLineStyle = { stroke: "#bf7df5" };

  function nodeDoubleClick(event, node) {
    setCurrTask(node);
    setTask(node);
    setOpenTaskConfig(true);
  }

  const onSave = async () => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      const response = await backendApi.put(`/pipeline/${pipeline.uuid}`, {
        reactflow_props: flow,
      });
      setPipeline(response.data.pipeline);
    }
  };

  const onExecute = async () => {
    const response = await backendApi.get(
      `/pipeline/${pipeline.uuid}/execute`,
      {
        timeout: 0,
      }
    );
    setPipeline(response.data.pipeline);
  };

  const onRestore = () => {
    const restoreFlow = () => {
      const flow = pipeline.reactflow_props;

      if (Object.keys(flow).length != 0) {
        const { x = 0, y = 0, zoom = 0.8 } = flow.viewport;
        setNodes(flow.nodes || []);
        setEdges(flow.edges || []);
        setViewport({ x, y, zoom });
      }
    };

    restoreFlow();
  };

  const onAdd = async (type, name) => {
    const response = await backendApi.post(`/pipeline/${pipeline.uuid}/task`, {
      name: name,
      task_type: type,
    });

    setPipeline(response.data.pipeline);
  };

  const onNodeDelete = async (node) => {
    try {
      const response = await backendApi.delete(
        `/pipeline/${pipeline.uuid}/task/${node[0].id}`
      );
      setPipeline(response.data.pipeline);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <>
      <SubHeader
        pipeline={pipeline}
        onExecute={onExecute}
        onSave={onSave}
        onAdd={onAdd}
        onRestore={onRestore}
        flowInstance={rfInstance}
      />
      <Flex style={{ paddingTop: "0.5rem" }}>
        <Flex style={{ height: "75vh", width: "100%" }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            defaultEdgeOptions={edgeOptions}
            connectionLineStyle={connectionLineStyle}
            nodeTypes={nodeTypes}
            onConnect={onConnect}
            onInit={setRfInstance}
            onNodesDelete={(node) => onNodeDelete(node)}
            onNodeDoubleClick={nodeDoubleClick}
            fitView
            fitViewOptions={{ maxZoom: 1, padding: 1 }}
          >
            <Controls />

            <Background variant="cross" gap={12} size={1} color="gray" />
          </ReactFlow>
        </Flex>
      </Flex>
      {currTask && (
        <Drawer
          title={
            <Space size={60}>
              <Button
                shape="circle"
                type="text"
                icon={<CloseOutlined />}
                onClick={() => {
                  setCurrTask(null);
                  setOpenTaskConfig(false);
                }}
              ></Button>
              <Space size="middle">
                <Typography.Text style={{ fontSize: 15, color: "#bfbfbf" }}>
                  {currTask.id}
                </Typography.Text>
                <SettingOutlined />
              </Space>
            </Space>
          }
          closeIcon={false}
          placement={"right"}
          width={"90%"}
          onClose={() => {
            setCurrTask(null);
            setOpenTaskConfig(false);
          }}
          open={openTaskConfig}
          styles={{
            content: {
              borderRadius: "40px 0 0 40px",
            },
            header: { borderBottomWidth: 0 },
          }}
          destroyOnClose={true}
        >
          {currTask.data.type === "data_loader" && (
            <SorceNodeConfig setOpenTaskConfig={setOpenTaskConfig} />
          )}
          {currTask.data.type === "data_transformer" && (
            <TransformNodeConfig setOpenTaskConfig={setOpenTaskConfig} />
          )}
          {currTask.data.type === "data_sink" && (
            <SinkNodeConfig setOpenTaskConfig={setOpenTaskConfig} />
          )}
        </Drawer>
      )}
    </>
  );
};

MainFlow.propTypes = {
  pipeline: propTypes.any,
  setPipeline: propTypes.func,
};

function EditWorkbook() {
  const [{ pipeline }, { setPipeline }] = pipelineStore();

  return (
    <Flex vertical style={{ padding: "0 1rem 0 1rem" }}>
      <ReactFlowProvider>
        <MainFlow pipeline={pipeline} setPipeline={setPipeline} />
      </ReactFlowProvider>
    </Flex>
  );
}

export default EditWorkbook;
