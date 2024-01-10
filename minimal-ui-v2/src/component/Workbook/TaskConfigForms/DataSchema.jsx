import { Button, Flex, Table, Typography, message } from "antd";
import { useState } from "react";
import { backendApi } from "../../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../../appState/pipelineStore";
import { taskStore } from "../../../appState/taskStore";

function DataSchema() {
  // const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [{ pipeline }, { setPipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const [messageApi, contextHolder] = message.useMessage();

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
    },
    {
      title: "Nullable",
      dataIndex: "nullable",
      render: (text) => (
        <>
          {text ? (
            <Typography style={{ color: "green", textTransform: "capitalize" }}>
              true
            </Typography>
          ) : (
            <Typography style={{ color: "red", textTransform: "capitalize" }}>
              false
            </Typography>
          )}
        </>
      ),
    },
    {
      title: "Type",
      dataIndex: "type",
    },
    {
      title: "Metadata",
      dataIndex: "metadata",
    },
  ];

  const getData = async () => {
    try {
      setLoading(true);

      if (currTask.status !== "executed") {
        try {
          const response = await backendApi.get(
            `pipeline/${pipeline.uuid}/task/${currTask.uuid}/execute`,
            {
              timeout: 0,
            }
          );
          setPipeline(response.data.pipeline);
        } catch (error) {
          console.log(error);
          messageApi.error(error.response.data.error[0]);
        }
      }

      const response = await backendApi.get(
        `pipeline/${pipeline.uuid}/task/${currTask.uuid}/sample_data`
      );

      setData(
        response.data.columns.map((item) => ({
          key: item.name,
          name: item.name,
          nullable: item.nullable,
          type: item.type,
          metadata: item.metadata,
        }))
      );
      setLoading(false);
    } catch (error) {
      setLoading(false);
      messageApi.error(error.response.data.error[0]);
      console.log(error);
    }
  };

  // const onSelectChange = (newSelectedRowKeys) => {
  //   console.log("selectedRowKeys changed: ", newSelectedRowKeys);
  //   setSelectedRowKeys(newSelectedRowKeys);
  // };

  // const rowSelection = {
  //   selectedRowKeys,
  //   onChange: onSelectChange,
  // };

  return (
    <Flex vertical style={{ margin: "1rem 1rem 1rem 1rem" }}>
      {contextHolder}
      <Flex>
        <Button type="primary" loading={loading} onClick={getData}>
          Infer Schema
        </Button>
      </Flex>
      <Flex style={{ paddingTop: "1rem" }}>
        <Table
          pagination={false}
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={data}
          scroll={{
            y: 400,
          }}
        />
      </Flex>
    </Flex>
  );
}

export default DataSchema;
