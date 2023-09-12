/* eslint-disable react/prop-types */
import { Icon } from '@iconify/react';
import { Tooltip } from '@mui/material';
import { useState } from 'react';
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from 'reactflow';
import { pipelineStore } from "../../appState/pipelineStore";
import DataDialogs from '../../components/TaskDataTable';
// const onEdgeClick = (evt, id) => {
//   evt.stopPropagation();
  
// }

export default function CustomEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
}) {
  const xEqual = sourceX === targetX;
  const yEqual = sourceY === targetY;
  const [{pipeline},] = pipelineStore()
  const [openDialog,setOpenDialog] = useState(false)
  const [edgePath, labelX, labelY] = getBezierPath({
    // we need this little hack in order to display the gradient for a straight line
    sourceX: xEqual ? sourceX + 0.0001 : sourceX,
    sourceY: yEqual ? sourceY + 0.0001 : sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              fontSize: 12,
              pointerEvents: 'all',
            }}
            className="nodrag nopan"
          >
            {
              pipeline.tasks[id.split('-')[1]].status === 'executed'? 
                <Tooltip title="Click to view sample records"><button className="edgebutton" onClick={() => setOpenDialog(true)}>
                  <Icon icon="mdi:graph-box-outline" style={{width:"20px",height:"20px"}}/>
                </button></Tooltip> :
                <Tooltip title="Execute the pipeline to load the data"><button className="edgebutton" onClick={() => setOpenDialog(false)}>
                  <Icon icon="ic:outline-cancel" style={{width:"20px",height:"20px"}}/>
                </button></Tooltip>
            }
            {openDialog && <DataDialogs open={openDialog} setOpen={setOpenDialog} task={id.split('-')[1]}/>}
          </div>
        </EdgeLabelRenderer>
      </>
  )
}
