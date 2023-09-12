import { Box, Typography } from '@mui/material'
import propTypes from 'prop-types'
import SinkConfig from '../../components/AppSideBar/SinkConfig'
import SourceConfig from '../../components/AppSideBar/SourceConfig'
import TransformConfig from '../../components/AppSideBar/TransformConfig'


AppSidebar.propTypes = {
    currNode: propTypes.object,
    closeBar: propTypes.func
}

function AppSidebar({currNode, closeBar}) {

    return (
        <Box sx={{ width: 400,paddingTop:2 }} role="presentation">
            <Typography variant='h4' align="center" sx={{ mb: 5 }}>Configure Task</Typography>
            {currNode.data.type === 'input' && <SourceConfig closeBar={closeBar} currNode={currNode}/>}
            {currNode.data.type === 'default' && <TransformConfig closeBar={closeBar} currNode={currNode}/>}
            {currNode.data.type === 'output' && <SinkConfig closeBar={closeBar} currNode={currNode}/>}
        </Box>
    )
}

export default AppSidebar

