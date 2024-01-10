// import { EyeTwoTone, SettingTwoTone } from "@ant-design/icons";
import { Button, Steps, message, theme } from "antd";
import propTypes from "prop-types";
import { useState } from "react";
import { backendApi } from "../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import { taskStore } from "../../appState/taskStore";
import PreviewData from "./PreviewData";
import DataSchema from "./TaskConfigForms/DataSchema";
import SelectSourceTarget from "./TaskConfigForms/SelectSourceTarget";
import SourceTargetConfig from "./TaskConfigForms/SourceTargetConfig";

SorceNodeConfig.propTypes = {
  setOpenTaskConfig: propTypes.func,
};

function SorceNodeConfig({ setOpenTaskConfig }) {
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const { token } = theme.useToken();
  const [taskConfig, setTaskConfig] = useState({});
  const [current, setCurrent] = useState(0);
  const [messageApi, contextHolder] = message.useMessage();

  const steps = [
    {
      title: "Type",
      content: (
        <SelectSourceTarget
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
        />
      ),
    },
    {
      title: "Properties",
      content: (
        <SourceTargetConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
        />
      ),
    },
    {
      title: "Schema",
      content: <DataSchema />,
    },
    {
      title: "Preview",
      content: <PreviewData />,
    },
  ];

  const next = async () => {
    if (current == 1) {
      try {
        const response = await backendApi.put(
          `/pipeline/${pipeline.uuid}/task/${currTask.uuid}`,
          { config_properties: taskConfig }
        );
        setPipeline(response.data.pipeline);
        messageApi.success("Configuration saved for the task");
      } catch (error) {
        console.log(error);
        messageApi.error(error.response.data.error[0]);
      }
    }
    setCurrent(current + 1);
  };

  const prev = () => {
    setCurrent(current - 1);
  };

  const items = steps.map((item) => ({
    key: item.title,
    title: item.title,
  }));

  const contentStyle = {
    minHeight: "80%",
    color: token.colorTextTertiary,
    backgroundColor: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    border: `1px dashed ${token.colorBorder}`,
    marginTop: 16,
  };

  return (
    <>
      {contextHolder}
      <Steps current={current} items={items} />
      <div style={contentStyle}>{steps[current].content}</div>
      <div
        style={{
          marginTop: 24,
        }}
      >
        {current < steps.length - 1 && (
          <Button type="primary" onClick={() => next()}>
            Next
          </Button>
        )}
        {current === steps.length - 1 && (
          <Button
            type="primary"
            onClick={() => {
              setOpenTaskConfig(false);
            }}
          >
            Done
          </Button>
        )}
        {current > 0 && (
          <Button
            style={{
              margin: "0 8px",
            }}
            onClick={() => prev()}
          >
            Previous
          </Button>
        )}
      </div>
    </>
  );
}
export default SorceNodeConfig;
