import { Button, Steps, message, theme } from "antd";
import propTypes from "prop-types";
import { useState } from "react";
import { backendApi } from "../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import { taskStore } from "../../appState/taskStore";
import SelectTransformation from "./TaskConfigForms/SelectTransformation";
import TransformConfig from "./TaskConfigForms/TransformConfig";

TransformNodeConfig.propTypes = {
  setOpenTaskConfig: propTypes.func,
};

function TransformNodeConfig({ setOpenTaskConfig }) {
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const { token } = theme.useToken();
  const [taskConfig, setTaskConfig] = useState({});
  const [current, setCurrent] = useState(0);
  const [buttonDisable, setButtonDisabled] = useState(true);
  const [messageApi, contextHolder] = message.useMessage();

  const steps = [
    {
      content: (
        <SelectTransformation
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      ),
    },
    {
      content: (
        <TransformConfig
          taskConfig={taskConfig}
          setTaskConfig={setTaskConfig}
          setButtonDisabled={setButtonDisabled}
        />
      ),
    },
  ];

  const next = async () => {
    setCurrent(current + 1);
    setButtonDisabled(true);
  };

  const prev = () => {
    setCurrent(current - 1);
    setButtonDisabled(true);
  };

  const saveConfig = async () => {
    console.log(taskConfig);
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
    setButtonDisabled(true);
    setOpenTaskConfig(false);
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
          <Button
            type="primary"
            onClick={() => next()}
            disabled={buttonDisable}
          >
            Next
          </Button>
        )}
        {current === steps.length - 1 && (
          <Button
            type="primary"
            onClick={() => {
              saveConfig();
            }}
            disabled={buttonDisable}
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

export default TransformNodeConfig;
