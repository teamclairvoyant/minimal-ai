import { EditOutlined } from "@ant-design/icons";
import { Flex, Tabs, Typography } from "antd";
import propTypes from "prop-types";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";
import SourceSchema from "./SourceSchema";

AggregateConfig.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

function AggregateConfig({ taskConfig, setTaskConfig, setButtonDisabled }) {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];

  const tabItem = [
    {
      key: "1",
      label: "Expressions",
      children: <p>Expressions</p>,
    },
    {
      key: "2",
      label: "Group By",
      children: <p>Group</p>,
    },
  ];

  return (
    <Flex vertical style={{ padding: "1rem 1rem 1rem 1rem" }}>
      <Flex gap="middle">
        <Typography.Text style={{ fontSize: 15 }}>
          {taskConfig.type.toUpperCase()}
        </Typography.Text>
        <EditOutlined style={{ fontSize: 20 }} />
      </Flex>

      <Flex>
        <SourceSchema />
        <Flex
          vertical
          gap={"small"}
          style={{
            padding: "1rem 1rem 0 2rem",
            width: "70%",
          }}
        >
          <Tabs defaultActiveKey="1" items={tabItem} />
        </Flex>
      </Flex>
    </Flex>
  );
}

export default AggregateConfig;
