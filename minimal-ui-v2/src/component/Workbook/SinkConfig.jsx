import { Flex } from "antd";
import propTypes from "prop-types";

SinkConfig.propTypes = {
  task: propTypes.object,
};

function SinkConfig({ task }) {
  return (
    <Flex vertical>
      <p>{task.id}</p>
    </Flex>
  );
}

export default SinkConfig;
