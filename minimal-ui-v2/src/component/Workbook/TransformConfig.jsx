import { Button, Form, Select, Space } from "antd";
import propTypes from "prop-types";
import { useState } from "react";
import { backendApi } from "../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import FilterConfigForm from "./TaskConfigForms/FilterConfigForm";
import JoinConfigForm from "./TaskConfigForms/JoinConfigForm";

const transformationType = [
  {
    label: "Filter",
    value: "filter",
  },
  {
    label: "Join",
    value: "join",
  },
  {
    label: "Custom SQL",
    value: "custom_sql",
  },
];

TransformConfig.propTypes = {
  task: propTypes.object,
  setCloseForm: propTypes.func,
};

function TransformConfig({ task, setCloseForm }) {
  const [form] = Form.useForm();
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const currTask = pipeline.tasks[task.id];
  const [transformation, setTransformation] = useState("");

  const onChange = (value) => {
    setTransformation(value);
  };

  const filterOption = (input, option) =>
    (option?.label ?? "").toLowerCase().includes(input.toLowerCase());

  const onFinish = async (values) => {
    try {
      const config_type = values.type;
      delete values.type;

      const response = await backendApi.put(
        `/pipeline/${pipeline.uuid}/task/${task.id}`,
        {
          config_type: config_type,
          config_properties: { ...values },
        }
      );
      setPipeline(response.data.pipeline);
      form.resetFields();
      setCloseForm(false);
      setTransformation("");
    } catch (error) {
      console.log("Failed:", error);
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };

  const formItemLayout = {
    labelCol: {
      xs: {
        span: 24,
      },
      sm: {
        span: 6,
      },
    },
    wrapperCol: {
      xs: {
        span: 24,
      },
      sm: {
        span: 14,
      },
    },
  };

  return (
    <Form
      {...formItemLayout}
      style={{
        maxWidth: 600,
      }}
      autoComplete="off"
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      form={form}
      name="transformConfig"
    >
      <Form.Item
        label="Type"
        name="type"
        tooltip="Select the transformation type"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the transformation type.",
          },
        ]}
      >
        <Select
          showSearch
          optionFilterProp="children"
          placeholder="Transformation"
          onChange={onChange}
          filterOption={filterOption}
          options={transformationType}
        />
      </Form.Item>
      {transformation === "filter" && <FilterConfigForm currTask={currTask} />}
      {transformation === "join" && <JoinConfigForm currTask={currTask} />}
      <Form.Item
        wrapperCol={{
          offset: 8,
          span: 16,
        }}
      >
        <Space direction="horizontal">
          <Button
            onClick={() => {
              form.resetFields();
              setCloseForm(false);
              setTransformation("");
            }}
          >
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}

export default TransformConfig;
