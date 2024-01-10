import { Flex } from "antd";
import propTypes from "prop-types";
import FileConfig from "./FileConfig";
import RDBMSConfig from "./RDBMSConfig";

SourceTargetConfig.propTypes = {
  setTaskConfig: propTypes.func,
  taskConfig: propTypes.object,
  setButtonDisabled: propTypes.func,
};

function SourceTargetConfig({ taskConfig, setTaskConfig, setButtonDisabled }) {
  return (
    <Flex style={{ paddingTop: "1rem", paddingLeft: "1rem" }}>
      {(taskConfig.source_target_area === "local_file" ||
        taskConfig.source_target_area === "gcp_bucket") && (
        <FileConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      )}
      {taskConfig.type === "mysql" && (
        <RDBMSConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      )}
    </Flex>
  );
}

export default SourceTargetConfig;
