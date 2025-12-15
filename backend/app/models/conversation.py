"""
对话和消息模型
"""
from datetime import datetime
from app.extensions import db


class Conversation(db.Model):
    """对话模型"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)  # 对话标题（通常是第一条用户消息的摘要）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = db.relationship('User', backref=db.backref('conversations', lazy=True, cascade='all, delete-orphan'))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan', order_by='Message.created_at')
    
    def to_dict(self, include_messages=False):
        """
        转换为字典（用于 API 返回）
        
        Args:
            include_messages: 是否包含消息列表
            
        Returns:
            dict: 对话信息字典
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': (self.created_at.isoformat() + 'Z') if self.created_at else None,
            'updated_at': (self.updated_at.isoformat() + 'Z') if self.updated_at else None,
            'message_count': len(self.messages) if self.messages else 0
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        
        return data
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.title}>'


class Message(db.Model):
    """消息模型"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' 或 'assistant'
    content = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)  # JSON 字符串，存储 RAG 来源信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """
        转换为字典（用于 API 返回）
        
        Returns:
            dict: 消息信息字典
        """
        import json
        sources = None
        if self.sources:
            try:
                sources = json.loads(self.sources)
            except (json.JSONDecodeError, TypeError):
                sources = []
        
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'sources': sources,
            'created_at': (self.created_at.isoformat() + 'Z') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id}: {self.role}>'

