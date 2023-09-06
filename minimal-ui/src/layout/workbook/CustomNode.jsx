/* eslint-disable react/prop-types */
import  { memo } from 'react';
import { Handle, Position } from 'reactflow';


const CustomNode = memo(({ data }) => {
  return (
    <>
      <div className="wrapper gradient">
        <div className="inner">
          <div className="body">
            {data.icon && <div className="icon">{data.icon}</div>}
            <div>
              <div className="title">{data.title}</div>
              {data.subline && <div className="subline">{data.subline}</div>}
            </div>
          </div>
          {data.type == "input"? 
            <Handle type="source" position={Position.Right} /> :
            data.type == "output"?
            <Handle type="target" position={Position.Left} /> :
            <>
            <Handle type="source" position={Position.Right} />
            <Handle type="target" position={Position.Left} />
            </>}
          
          
        </div>
      </div>
    </>
  );
});
CustomNode.displayName = "CustomNode";
export default CustomNode;