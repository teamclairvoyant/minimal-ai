import { Form, Input, Select } from "antd";
import propTypes from "prop-types";

const FileType = [
  {
    label: "CSV",
    value: "csv",
  },
  {
    label: "JSON",
    value: "json",
  },
  {
    label: "PARQUET",
    value: "parquet",
  },
];

FileConfigForm.propTypes = {
  currTask: propTypes.object,
};
function FileConfigForm({ currTask }) {
  return (
    <>
      <Form.Item
        label="File Type"
        name="file_type"
        tooltip="Type of file"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the file type",
          },
        ]}
      >
        <Select
          placeholder="File type"
          optionFilterProp="children"
          options={FileType}
        />
      </Form.Item>
      <Form.Item
        label="File Path"
        name="file_path"
        tooltip="Path of file"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the path to file",
          },
        ]}
      >
        <Input placeholder="File path" />
      </Form.Item>
    </>
  );
}

export default FileConfigForm;
