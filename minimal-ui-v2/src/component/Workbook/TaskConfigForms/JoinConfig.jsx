import { EditOutlined, MinusOutlined, PlusOutlined } from "@ant-design/icons";
import {
  Button,
  Flex,
  Input,
  Menu,
  Select,
  Tabs,
  Typography,
  message,
} from "antd";
import propTypes from "prop-types";
import { useEffect, useState } from "react";
import { backendApi } from "../../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";
import { formatNodeName } from "../../../utils/formatString";

const JoinType = [
  {
    label: "Left Join",
    value: "left",
  },
  {
    label: "Right Join",
    value: "right",
  },
  {
    label: "Full Join",
    value: "full",
  },
  {
    label: "Inner Join",
    value: "inner",
  },
  {
    label: "Cross Join",
    value: "cross",
  },
];

function getItem(name, type) {
  return {
    key: name,
    label: (
      <Flex gap={"middle"} style={{ justifyContent: "space-between" }}>
        <Typography.Text>{name}</Typography.Text>
        <Typography.Text>{type}</Typography.Text>
      </Flex>
    ),
  };
}

JoinConfig.propTypes = {
  taskConfig: propTypes.object,
  setTaskConfig: propTypes.func,
  setButtonDisabled: propTypes.func,
};

function JoinConfig({ taskConfig, setTaskConfig, setButtonDisabled }) {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const [schema1, setSchema1] = useState([]);
  const [schema2, setSchema2] = useState([]);
  const [messageApi, contextHolder] = message.useMessage();
  const [rowNum, setRowNum] = useState([1]);
  const [targetCol, setTargetCol] = useState({});

  useEffect(() => {
    const fetch_schema = async () => {
      try {
        const response1 = await backendApi.get(
          `/pipeline/${pipeline.uuid}/task/${currTask.upstream_tasks[0]}/sample_data?schema=true`
        );
        setSchema1(response1.data.columns);
      } catch (error) {
        console.log(error);
        messageApi.error(error.response.data.error[0]);
      }
      try {
        const response2 = await backendApi.get(
          `/pipeline/${pipeline.uuid}/task/${currTask.upstream_tasks[1]}/sample_data?schema=true`
        );
        setSchema2(response2.data.columns);
      } catch (error) {
        console.log(error);
        messageApi.error(error.response.data.error[0]);
      }
    };
    fetch_schema();
    setTaskConfig({ ...taskConfig, how: "inner", target_columns: {} });
  }, []);

  function getSubMenu() {
    return [
      {
        key: formatNodeName(currTask.upstream_tasks[0]),
        label: currTask.upstream_tasks[0],
        children: schema1.map((item) => {
          return getItem(item.name, item.type);
        }),
      },
      {
        key: formatNodeName(currTask.upstream_tasks[1]),
        label: currTask.upstream_tasks[1],
        children: schema2.map((item) => {
          return getItem(item.name, item.type);
        }),
      },
    ];
  }

  function addColumn() {
    const len = rowNum.length + 1;
    setRowNum((rowNum) => [...rowNum, len]);
  }
  const tabItem = [
    {
      key: "1",
      label: "Conditions",
      children: (
        <Flex vertical gap="6rem">
          <Flex gap={"large"}>
            <Flex gap={"large"} vertical>
              <Flex gap={"large"}>
                <Flex vertical gap={"small"}>
                  <Typography.Text>Left Dataset</Typography.Text>
                  <Input
                    placeholder="Enter left dataset name"
                    onChange={(e) =>
                      setTaskConfig({
                        ...taskConfig,
                        left_table: e.target.value,
                      })
                    }
                  />
                </Flex>
                <Flex vertical gap={"small"}>
                  <Typography.Text>Right Dataset</Typography.Text>
                  <Input
                    placeholder="Enter right dataset name"
                    onChange={(e) =>
                      setTaskConfig({
                        ...taskConfig,
                        right_table: e.target.value,
                      })
                    }
                  />
                </Flex>
              </Flex>
              <Flex vertical gap={"small"}>
                <Typography.Text>Join Conditions</Typography.Text>
                <Input
                  style={{ width: "24rem" }}
                  placeholder="Enter the join condition"
                  onChange={(e) =>
                    setTaskConfig({ ...taskConfig, on: e.target.value })
                  }
                />
              </Flex>
            </Flex>
            <Flex vertical gap={"small"} style={{ padding: "0 0 0 3rem" }}>
              <Typography.Text>Join Type</Typography.Text>
              <Select
                style={{ width: "10rem" }}
                defaultValue={"inner"}
                options={JoinType}
                onChange={(e) => setTaskConfig({ ...taskConfig, how: e })}
              ></Select>
            </Flex>
          </Flex>
          <Flex vertical gap={"small"}>
            <Typography.Text>where clause</Typography.Text>
            <Input
              style={{ width: "39rem" }}
              placeholder="Enter the where condition"
              onChange={(e) =>
                setTaskConfig({ ...taskConfig, where: e.target.value })
              }
            />
          </Flex>
        </Flex>
      ),
    },
    {
      key: "2",
      label: "Expressions",
      children: (
        <Flex vertical gap={"middle"}>
          <Flex gap="7rem">
            <Typography.Text>Target Column</Typography.Text>
            <Typography.Text>Expression</Typography.Text>
            <Flex gap={"middle"} style={{ marginLeft: "5rem" }}>
              <Button
                icon={<PlusOutlined />}
                size="small"
                style={{ backgroundColor: "#424040" }}
                onClick={addColumn}
              >
                Add
              </Button>
              <Button
                icon={<MinusOutlined />}
                size="small"
                style={{ backgroundColor: "#424040" }}
                onClick={() => {
                  if (rowNum.length > 1) {
                    rowNum.pop();
                    setRowNum((rowNum) => [...rowNum]);
                  }
                }}
              >
                Delete
              </Button>
            </Flex>
          </Flex>
          <Flex
            vertical
            gap={"small"}
            style={{
              position: "sticky",
              overflowY: "auto",
              minHeight: "20rem",
              maxHeight: "20rem",
              padding: "0 2rem 0 0",
            }}
          >
            {rowNum.map((i) => (
              <Flex key={i} gap="5rem">
                <Input
                  bordered={false}
                  placeholder="Target col..."
                  style={{ width: "10rem", borderBottom: "1px solid #424040" }}
                  onChange={(e) => setTargetCol(e.target.value)}
                ></Input>
                <Input
                  bordered={false}
                  style={{ borderBottom: "1px solid #424040" }}
                  placeholder="Expression"
                  onChange={(e) => {
                    setTaskConfig((taskConfig) => ({
                      ...taskConfig,
                      target_columns: {
                        ...taskConfig.target_columns,
                        [targetCol]: e.target.value,
                      },
                    }));
                    setButtonDisabled(false);
                  }}
                ></Input>
              </Flex>
            ))}
          </Flex>
        </Flex>
      ),
    },
  ];

  return (
    <Flex vertical style={{ padding: "1rem 1rem 1rem 1rem" }}>
      {contextHolder}
      <Flex gap="middle">
        <Typography.Text style={{ fontSize: 15 }}>
          {taskConfig.type.toUpperCase()}
        </Typography.Text>
        <EditOutlined style={{ fontSize: 20 }} />
      </Flex>

      <Flex>
        <Flex
          vertical
          gap="small"
          style={{
            padding: "1rem 1rem 1rem 1rem",
            borderRight: "1px solid #424040",
          }}
        >
          <Flex>
            <Typography.Text
              style={{ fontSize: 20, color: "#fefefe", paddingLeft: "2rem" }}
            >
              Input
            </Typography.Text>
          </Flex>

          <Flex
            style={{
              position: "sticky",
              overflowY: "auto",
              minHeight: "20rem",
              maxHeight: "20rem",
              padding: "1rem 0 0 0",
            }}
          >
            <Menu
              mode="inline"
              items={getSubMenu()}
              style={{
                width: "25rem",
                backgroundColor: "inherit",
                borderRight: "0",
              }}
              selectable={false}
            />
          </Flex>
        </Flex>
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

export default JoinConfig;
