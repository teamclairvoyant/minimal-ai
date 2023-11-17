import { Form, Input } from "antd";

function FilterConfigForm() {
  return (
    <Form.Item
      label="Filter"
      name="filter"
      tooltip="Condition to filter on"
      hasFeedback
      rules={[
        {
          required: true,
          message: "Enter the filter condition",
        },
      ]}
    >
      <Input placeholder="Filter clause" />
    </Form.Item>
  );
}

export default FilterConfigForm;
