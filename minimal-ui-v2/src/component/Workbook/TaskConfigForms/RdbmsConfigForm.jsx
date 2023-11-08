import { Form, Input } from "antd";
import propTypes from "prop-types";

RdbmsConfigForm.propTypes = {
  currTask: propTypes.object,
};

function RdbmsConfigForm({ currTask }) {
  return (
    <>
      <Form.Item
        label="Host"
        name="host"
        tooltip="Hostname of the server"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the hostname",
          },
        ]}
      >
        <Input placeholder="127.0.0.1" />
      </Form.Item>
      <Form.Item
        label="Port"
        name="port"
        tooltip="port number"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the port number",
          },
        ]}
      >
        <Input placeholder="3306" />
      </Form.Item>
      <Form.Item
        label="User"
        name="user"
        tooltip="User Id"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the user id",
          },
        ]}
      >
        <Input placeholder="User Id" />
      </Form.Item>
      <Form.Item
        label="Password"
        name="password"
        tooltip="Password"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the password",
          },
        ]}
      >
        <Input.Password placeholder="*********" />
      </Form.Item>
      <Form.Item
        label="Schema"
        name="database"
        tooltip="Schema name"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the schema name",
          },
        ]}
      >
        <Input placeholder="schema" />
      </Form.Item>
      <Form.Item
        label="Table"
        name="table"
        tooltip="Table name"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the table name",
          },
        ]}
      >
        <Input placeholder="tablename" />
      </Form.Item>
    </>
  );
}

export default RdbmsConfigForm;
