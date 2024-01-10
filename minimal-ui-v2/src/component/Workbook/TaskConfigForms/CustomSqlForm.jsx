import { Form, Input } from "antd";

function CustomSqlForm() {
  return (
    <Form.Item
      label="Custom Sql"
      name="query"
      tooltip="sql to run on the data"
      hasFeedback
      rules={[
        {
          required: true,
          message: "Enter the sql query",
        },
      ]}
    >
      <Input placeholder="Sql query" />
    </Form.Item>
  );
}

export default CustomSqlForm;
