import { Icon } from "@iconify/react";
import { Flex, Typography } from "antd";
import propTypes from "prop-types";
import { memo } from 'react';
import { Handle, Position } from 'reactflow';

const CustomNode = memo(({ data }) => {

  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#555' }}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={true}
      />
      <Flex align="center">
        <Flex style={{padding: "1rem 0 1rem 1rem", height: "100%", width: "100%"}} align="center">
            <Typography style={{color:"black",fontSize:20}}>{data.title}</Typography>
        </Flex>
        <Flex style={{padding: "0 1rem 0 1rem"}} align="center">
            <Icon icon={data.icon} width={30}></Icon>
        </Flex>
      </Flex>
      
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#555' }}
        isConnectable={true}
      />
    </>
  );
});

CustomNode.propTypes = {
    data: propTypes.object
}

CustomNode.displayName = "CustomNode";
export default CustomNode;