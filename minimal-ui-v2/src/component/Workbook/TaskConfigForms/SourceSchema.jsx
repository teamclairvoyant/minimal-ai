import { Flex, Menu, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { backendApi } from "../../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";
import { formatNodeName } from "../../../utils/formatString";

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

function SourceSchema() {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const [schema, setSchema] = useState([]);
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    const fetch_schema = async () => {
      try {
        const response1 = await backendApi.get(
          `/pipeline/${pipeline.uuid}/task/${currTask.upstream_tasks[0]}/sample_data?schema=true`
        );
        setSchema(response1.data.columns);
      } catch (error) {
        console.log(error);
        messageApi.error(error.response.data.error[0]);
      }
    };
    fetch_schema();
  }, []);

  function getSubMenu() {
    return [
      {
        key: formatNodeName(currTask.upstream_tasks[0]),
        label: currTask.upstream_tasks[0],
        children: schema.map((item) => {
          return getItem(item.name, item.type);
        }),
      },
    ];
  }

  return (
    <>
      {contextHolder}
      {currTask && (
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
      )}
    </>
  );
}

export default SourceSchema;
