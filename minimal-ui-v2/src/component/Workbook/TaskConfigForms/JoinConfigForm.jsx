import { Form, Select } from "antd";
import propTypes from "prop-types";
import { useState } from "react";

const JoinType = [
  {
    label: "Left Join",
    value: "left_join",
  },
  {
    label: "Right Join",
    value: "right_join",
  },
  {
    label: "Full Join",
    value: "full_join",
  },
  {
    label: "Inner Join",
    value: "inner_join",
  },
  {
    label: "Cross Join",
    value: "cross_join",
  },
];

const rightItems = ["col1", "col2", "col3", "col4"];

const leftItems = ["col1", "col2", "col3", "col4"];

JoinConfigForm.propTypes = {
  currTask: propTypes.object,
};

function JoinConfigForm({ currTask }) {
  console.log(currTask);
  const [rightOn, setRightOn] = useState([]);
  const [leftOn, setLeftOn] = useState([]);
  const filteredRight = rightItems.filter((o) => !rightOn.includes(o));
  const filteredLeft = leftItems.filter((o) => !leftOn.includes(o));
  return (
    <>
      <Form.Item
        label="Join Type"
        name="how"
        tooltip="Type of Join"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the join type",
          },
        ]}
      >
        <Select
          placeholder="Join type"
          optionFilterProp="children"
          options={JoinType}
        />
      </Form.Item>
      <Form.Item
        label="Right table"
        name="right_table"
        tooltip="Right Table"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the right table name",
          },
        ]}
      >
        <Select
          placeholder="Right table"
          optionFilterProp="children"
          options={
            currTask.upstream_tasks &&
            currTask.upstream_tasks.map((item) => ({
              value: item,
              lable: item,
            }))
          }
        />
      </Form.Item>
      <Form.Item
        label="Left table"
        name="left_table"
        tooltip="Left Table"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Enter the left table name",
          },
        ]}
      >
        <Select
          placeholder="Left table"
          optionFilterProp="children"
          options={
            currTask.upstream_tasks &&
            currTask.upstream_tasks.map((item) => ({
              value: item,
              lable: item,
            }))
          }
        />
      </Form.Item>
      <Form.Item
        label="Right On"
        name="right_on"
        tooltip="Select the columns from right table"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the columns from right table",
          },
        ]}
      >
        <Select
          mode="multiple"
          placeholder="select columns"
          value={rightOn}
          onChange={setRightOn}
          style={{
            width: "100%",
          }}
          options={filteredRight.map((item) => ({
            value: item,
            label: item,
          }))}
        />
      </Form.Item>
      <Form.Item
        label="Left On"
        name="left_on"
        tooltip="Select the columns from left table"
        hasFeedback
        rules={[
          {
            required: true,
            message: "Select the columns from left table",
          },
        ]}
      >
        <Select
          mode="multiple"
          placeholder="select columns"
          value={leftOn}
          onChange={setLeftOn}
          style={{
            width: "100%",
          }}
          options={filteredLeft.map((item) => ({
            value: item,
            label: item,
          }))}
        />
      </Form.Item>
    </>
  );
}

export default JoinConfigForm;
