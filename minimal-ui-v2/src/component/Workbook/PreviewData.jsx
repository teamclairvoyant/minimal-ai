import { Button, Flex, Table } from "antd";
import { useState } from "react";
import { backendApi } from "../../../../minimal-ui/src/api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import { taskStore } from "../../appState/taskStore";

function PreviewData() {
  const [{ pipeline }] = pipelineStore();
  const [{ task }] = taskStore();
  const currTask = pipeline.tasks[task.id];
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);

  const getData = async () => {
    const response = await backendApi.get(
      `/pipeline/${pipeline.uuid}/task/${currTask.uuid}/sample_data`
    );

    setColumns(getColumns(response.data.columns));
    setData(response.data.records);
  };

  const getColumns = (cols) =>
    cols.map((col) => ({ title: col.name, dataIndex: col.name }));

  return (
    <Flex vertical style={{ margin: "1rem 1rem 1rem 1rem" }}>
      <Flex>
        <Button type="primary" onClick={getData}>
          Preview Data
        </Button>
      </Flex>
      <Flex style={{ marginTop: "1rem" }}>
        <Table
          bordered
          virtual
          scroll={{
            x: 200,
            y: 250,
          }}
          pagination={true}
          columns={columns}
          dataSource={data}
        ></Table>
      </Flex>
    </Flex>
  );
}

export default PreviewData;
