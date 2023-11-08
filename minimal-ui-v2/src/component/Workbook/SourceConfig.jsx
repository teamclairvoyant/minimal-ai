import { Button, Form, Select, Space } from "antd";
import propTypes from "prop-types";
import { useState } from "react";
import { backendApi } from "../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import FileConfigForm from "./TaskConfigForms/FileConfigForm";
import RdbmsConfigForm from "./TaskConfigForms/RdbmsConfigForm";

const sourceType = [
  {
    label: "Local File",
    value: "local_file",
  },
  {
    label: "GCP Bucket",
    value: "gcp_bucket",
  },
  {
    label: "MYSQL",
    value: "mysql",
  },
];

SourceConfig.propTypes = {
  task: propTypes.object,
  setCloseForm: propTypes.func,
};

function SourceConfig({ task, setCloseForm }) {
  const [form] = Form.useForm();
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const currTask = pipeline.tasks[task.id];
  const [source, setSource] = useState("");

  const onChange = (value) => {
    setSource(value);
  };

  const filterOption = (input, option) =>
    (option?.label ?? "").toLowerCase().includes(input.toLowerCase());

  const onFinish = async (values) => {
    try {
      const config_type = values.source;
      delete values.source;

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
      // setSource("");
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
      name="sourceTaskConfig"
    >
      <Form.Item
        label="Source"
        name="source"
        tooltip="Select the source type"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the source type.",
          },
        ]}
      >
        <Select
          showSearch
          optionFilterProp="children"
          placeholder="Select Source"
          onChange={onChange}
          filterOption={filterOption}
          options={sourceType}
        />
      </Form.Item>
      {(source === "local_file" || source === "gcp_bucket") && (
        <FileConfigForm currTask={currTask} />
      )}
      {source === "mysql" && <RdbmsConfigForm currTask={currTask} />}
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
              setSource("");
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
export default SourceConfig;
