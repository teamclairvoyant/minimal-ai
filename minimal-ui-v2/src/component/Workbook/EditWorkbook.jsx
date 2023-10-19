import { Flex, Statistic } from "antd"
import { useEffect, useState } from "react"
import { backendApi } from "../../api/api"


const subBarStyle = {
  width: "100%",
  height: "3rem"
}


function EditWorkbook() {
  const [systemSummary, setSystemSummary] = useState({})

  useEffect(() => {
    async function getSummary() {
      const response = await backendApi.get("/cpu_ram_info",{timeout:5000})
      if (response.data) {
        setSystemSummary(response.data)
      }
    }
    getSummary()
  },[])

    return (
      <Flex vertical>
        <Flex style={subBarStyle}>
          <Statistic title="info" value={systemSummary.cpu} />
        </Flex>
      </Flex>
    )
  }
  
  export default EditWorkbook
  