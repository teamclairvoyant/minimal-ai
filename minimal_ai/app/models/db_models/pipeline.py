from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from minimal_ai.app.api.db import Base


class PipelineMeta(Base):
    __tablename__ = "pipeline_meta"

    pipeline_uuid = Column(String(500), primary_key=True, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    modified_by = Column(String(100))
    modified_at = Column(DateTime)

    def __repr__(self):
        return f'Pipeline(pipeline_uuid={self.pipeline_uuid}, created_by={self.created_by}, \
            created_at={self.created_at}, modified_by={self.modified_by}, modified_at={self.modified_at})'


class PipelineRunStatus(Base):
    __tablename__ = "pipeline_run_status"
    id = Column(Integer, primary_key=True, index=True, autoincrement='auto')
    pipeline_uuid = Column(String(80), ForeignKey(
        'pipeline_meta.pipeline_uuid'), nullable=False, unique=True)
    latest_run_status = Column(String(100), nullable=False)

    def __repr__(self):
        return f'PipelineStatus(name={self.pipeline_uuid}, latest_run_status={self.latest_run_status})'
