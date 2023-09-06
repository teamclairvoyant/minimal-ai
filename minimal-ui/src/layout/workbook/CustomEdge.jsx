/* eslint-disable react/prop-types */
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from 'reactflow';
import { Icon } from '@iconify/react';
import { pipelineStore } from "../../appState/pipelineStore";


const onEdgeClick = (evt, id) => {
  evt.stopPropagation();
  alert(`remove ${id}`);
}

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
              pipeline.tasks[id.split('-')[1]].configured ? 
                (<button className="edgebutton" onClick={(event) => onEdgeClick(event, id)}>
                  <Icon icon="mdi:graph-box-outline" style={{width:"20px",height:"20px"}}/>
                </button>) :
                (<button className="edgebutton" onClick={(event) => onEdgeClick(event, id)}>
                  <Icon icon="ic:outline-cancel" style={{width:"20px",height:"20px"}}/>
                </button>)
            }

          </div>
        </EdgeLabelRenderer>
      </>
  )
}
