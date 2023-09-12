/* eslint-disable react-hooks/exhaustive-deps */
import { Drawer } from '@mui/material';
import propTypes from "prop-types";
import { useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  Panel,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';
import { backendApi } from "../../api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import "../../assets/css/index.css";
import { formatNodeName } from '../../utils/formatString';
import SubBar from "../subBar";
import CustomEdge from './CustomEdge';
import CustomNode from './CustomNode';
import AppSidebar from './appSidebar';


const nodeTypes = {
  node: CustomNode,
};

const edgeTypes = {
  turbo: CustomEdge,
};

const MainFlow = ({pipeline, setPipeline}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rfInstance, setRfInstance] = useState(null);
  const { setViewport } = useReactFlow();
  const [currNode, setCurrNode] = useState();
  const [showAppBar, setShowAppBar] = useState(false)

  const onConnect = async (params) => {
    if (params){
      let payload = {
        "upstream_task_uuids" : [params.source]
      }
      const response = await backendApi.put(`/api/v1/pipeline/${pipeline.uuid}/task/${params.target}`,payload)
      console.log(response.data)
    }
    
    setEdges((eds) => addEdge(params, eds))
  }


  const edgeOptions = {
    animated: true,
    type: 'turbo',
    markerEnd: {type:MarkerType.ArrowClosed},
  };

  const connectionLineStyle = { stroke: '#bf7df5' };

  function nodeClick(event,node) {
    setCurrNode(node)
    setShowAppBar(!showAppBar)
  }


  const onSave = async () => {
    if (rfInstance) {
      const flow = rfInstance.toObject();
      const response = await backendApi.put(`/api/v1/pipeline/${pipeline.uuid}`,{
        "reactflow_props":flow
      })
      setPipeline(response.data.pipeline)
    }
  }

  const onExecute = async () => {
    await backendApi.get(`/api/v1/pipeline/${pipeline.uuid}/execute`)
  }



  const onRestore = () => {
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
  };


  const onAdd = async (type,name) => {
    const response = await backendApi.post(`/api/v1/pipeline/${pipeline.uuid}/task`,{
      "name": name,
      "task_type": type === 'input' ? 'data_loader' : type === 'output' ? 'data_sink' : 'data_transformer',
      "upstream_task_uuids": null
    })

    setPipeline(response.data.pipeline)
    let task = response.data.pipeline.tasks[formatNodeName(name)]
    const newNode = {
      id: task.uuid,
      data: { title: task.name, subline: '', type:`${type}` },
      type:'node',
      position: {
        x: Math.floor(Math.random() * 100),
        y: Math.floor(Math.random() * 100),
      },
    }

    setNodes((nds) => 
      nds.concat(newNode))
  }


  return (
    <>
      <SubBar onButtonClick={onAdd}></SubBar>
      <div style={{display:'flex',flexDirection: 'row-reverse',height:'inherit'}}>
        <div>
          <Drawer anchor='right' open={showAppBar} onClose={() => setShowAppBar(false)}>
            <AppSidebar currNode={currNode} closeBar={() => setShowAppBar(false)}></AppSidebar>
          </Drawer>
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          defaultEdgeOptions={edgeOptions}
          connectionLineStyle={connectionLineStyle}
          onConnect={onConnect}
          onInit={setRfInstance}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodeClick={nodeClick}
        >
          <Panel position="top-right">
            <button onClick={onExecute}>Execute</button>
            <button onClick={onSave}>save</button>
            <button onClick={onRestore}>restore</button>
          </Panel>
          <Controls/>
          <svg>
            <defs>
              <linearGradient id="edge-gradient">
                <stop offset="0%" stopColor="#ae53ba" />
                <stop offset="100%" stopColor="#2a8af6" />
              </linearGradient>

              <marker
                id="edge-circle"
                viewBox="-5 -5 10 10"
                refX="0"
                refY="0"
                markerUnits="strokeWidth"
                markerWidth="10"
                markerHeight="10"
                orient="auto"
              >
                <circle stroke="#2a8af6" strokeOpacity="0.75" r="2" cx="0" cy="0" />
              </marker>
            </defs>
          </svg>
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </div>
    </>
  )
}

MainFlow.propTypes = {
  pipeline: propTypes.any,
  setPipeline: propTypes.func
}


export default function AppFlow(){
  const [{pipeline},{setPipeline}] = pipelineStore()

  return (
      <div style={{ width: '100%', height: '100%'}}>
        <ReactFlowProvider>
          <MainFlow pipeline={pipeline} setPipeline={setPipeline}/>
        </ReactFlowProvider>
      </div>

  )
}