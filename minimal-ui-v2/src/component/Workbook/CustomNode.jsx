import { Icon } from "@iconify/react";
import { Flex, Typography } from "antd";
import propTypes from "prop-types";
import { memo } from "react";
import { Handle, Position } from "reactflow";

const CustomNode = memo(({ data }) => {
  return (
    <>
      {data.type !== "data_loader" && (
        <Handle
          type="target"
          position={Position.Left}
          style={{ background: "#555", width: 10, height: 10, left: -10 }}
          onConnect={(params) => console.log("handle onConnect", params)}
          isConnectable={true}
        />
      )}
      <Flex align="center">
        <Flex
          style={{
            padding: "1rem 1rem 1rem 1rem",
            height: "100%",
            width: "100%",
          }}
          align="center"
        >
          <Typography style={{ color: "white", fontSize: 20 }}>
            {data.title}
          </Typography>
        </Flex>
        <Flex
          style={{
            position: "absolute",
            top: "-9px",
            right: "-9px",
          }}
          align="center"
        >
          <Icon icon={data.icon} width={20}></Icon>
        </Flex>
      </Flex>

      {data.type !== "data_sink" && (
        <Handle
          type="source"
          position={Position.Right}
          style={{ background: "#555", width: 10, height: 10, right: -10 }}
          isConnectable={true}
        />
      )}
    </>
  );
});

CustomNode.propTypes = {
  data: propTypes.object,
};

CustomNode.displayName = "CustomNode";
export default CustomNode;
