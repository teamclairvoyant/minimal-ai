import {
  FolderOpenOutlined,
  InfoCircleOutlined,
  TagsOutlined,
} from "@ant-design/icons";
import { Flex, Input, Select, Tooltip, Typography } from "antd";
import propTypes from "prop-types";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";

FileConfig.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

const WriteMode = [
  {
    label: "Append",
    value: "append",
  },
  {
    label: "Overwrite",
    value: "overwrite",
  },
  {
    label: "Ignore",
    value: "ignore",
  },
  {
    label: "ErrorIfExists",
    value: "errorifexists",
  },
];

function FileConfig({ taskConfig, setTaskConfig, setButtonDisabled }) {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  return (
    <Flex vertical>
      <Flex vertical>
        <Typography.Text strong type="secondary">
          File Path:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="file_path"
            placeholder="Path to file"
            prefix={<FolderOpenOutlined className="site-form-item-icon" />}
            suffix={
              <Tooltip title="Enter the path where the file is located.">
                <InfoCircleOutlined
                  style={{
                    color: "rgb(255 255 255 / 45%)",
                  }}
                />
              </Tooltip>
            }
            size="large"
            onChange={(e) =>
              setTaskConfig({
                ...taskConfig,
                file_path: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "2rem" }}>
        <Typography.Text strong type="secondary">
          Extras:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="extras"
            placeholder="Extra options"
            prefix={<TagsOutlined className="site-form-item-icon" />}
            suffix={
              <Tooltip title="Extra properties in key value format.">
                <InfoCircleOutlined
                  style={{
                    color: "rgb(255 255 255 / 45%)",
                  }}
                />
              </Tooltip>
            }
            size="large"
            onChange={(e) =>
              setTaskConfig({
                ...taskConfig,
                extras: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      {currTask.task_type === "data_sink" && (
        <Flex vertical style={{ paddingTop: "2rem" }}>
          <Typography.Text strong type="secondary">
            Write Mode:
          </Typography.Text>
          <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
            <Select
              style={{
                width: "15rem",
              }}
              onChange={(e) => {
                setTaskConfig({
                  ...taskConfig,
                  mode: e,
                });
                setButtonDisabled(false);
              }}
              options={WriteMode}
            />
          </Flex>
        </Flex>
      )}
    </Flex>
  );
}

export default FileConfig;
