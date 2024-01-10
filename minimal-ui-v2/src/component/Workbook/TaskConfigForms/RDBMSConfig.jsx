// import { DatabaseOutlined, InfoCircleOutlined } from "@ant-design/icons";
import { InfoCircleOutlined } from "@ant-design/icons";
import { Flex, Input, Select, Tooltip, Typography } from "antd";
import propTypes from "prop-types";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";

RDBMSConfig.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
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

function RDBMSConfig({ taskConfig, setTaskConfig }) {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  return (
    <Flex vertical>
      <Flex vertical>
        <Typography.Text strong type="secondary">
          Host:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="host"
            placeholder="127.0.0.1"
            suffix={
              <Tooltip title="Enter the hostname of the server">
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
                host: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          Port:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="port"
            placeholder="3306"
            suffix={
              <Tooltip title="Enter the Port number of the server">
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
                port: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          User:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="user"
            placeholder="username"
            suffix={
              <Tooltip title="Enter the name of the user">
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
                user: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          Password:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input.Password
            id="password"
            placeholder="*********"
            suffix={
              <Tooltip title="Enter the password for the user">
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
                password: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          Schema:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="schema"
            placeholder="schema"
            suffix={
              <Tooltip title="Enter the schema name">
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
                database: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          Table:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="table"
            placeholder="table"
            suffix={
              <Tooltip title="Enter the name of the table">
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
                table: e.target.value,
              })
            }
          />
        </Flex>
      </Flex>
      <Flex vertical style={{ paddingTop: "1rem" }}>
        <Typography.Text strong type="secondary">
          Extras:
        </Typography.Text>
        <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
          <Input
            id="extras"
            placeholder="extra properties"
            suffix={
              <Tooltip title="Enter the extra properties in key value pair.">
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
        <Flex vertical style={{ paddingTop: "1rem", paddingBottom: "1rem" }}>
          <Typography.Text strong type="secondary">
            Write Mode:
          </Typography.Text>
          <Flex style={{ width: "50rem", paddingTop: "0.5rem" }}>
            <Select
              defaultValue="OVERWRITE"
              style={{
                width: "15rem",
              }}
              onChange={(e) =>
                setTaskConfig({
                  ...taskConfig,
                  mode: e.target.value,
                })
              }
              options={WriteMode}
            />
          </Flex>
        </Flex>
      )}
    </Flex>
  );
}

export default RDBMSConfig;
