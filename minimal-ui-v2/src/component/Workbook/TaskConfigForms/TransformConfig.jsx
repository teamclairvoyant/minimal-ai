import { Flex } from "antd";
import propTypes from "prop-types";
import JoinConfig from "./JoinConfig";
import AggregateConfig from "./AggregateConfig";

TransformConfig.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

function TransformConfig({ taskConfig, setTaskConfig, setButtonDisabled }) {
  return (
    <Flex vertical>
      {taskConfig && taskConfig.type === "join" && (
        <JoinConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      )}
      {taskConfig && taskConfig.type === "aggregate" && (
        <AggregateConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      )}
    </Flex>
  );
}

export default TransformConfig;
