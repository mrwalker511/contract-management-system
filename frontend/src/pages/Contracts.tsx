/**
 * Contracts Page - List and manage contracts
 */
import { useState, useEffect } from 'react';
import {
  Table, Button, Space, Tag, Input, Select, Modal, Form,
  message, Popconfirm, Typography, Card,
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { contractsAPI } from '../services/api';
import type { ContractResponse, ContractCreate, ContractStatus } from '../types/api';
import { useAuthStore } from '../contexts/AuthContext';
import dayjs from 'dayjs';

const { Title } = Typography;
const { TextArea } = Input;

const STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  pending_review: 'processing',
  under_review: 'processing',
  approved: 'success',
  pending_signature: 'warning',
  signed: 'success',
  active: 'success',
  expired: 'default',
  terminated: 'error',
  rejected: 'error',
};

export const ContractsPage = () => {
  const [contracts, setContracts] = useState<ContractResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState<ContractResponse | null>(null);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [form] = Form.useForm();
  const { user } = useAuthStore();

  useEffect(() => {
    loadContracts();
  }, [statusFilter]);

  const loadContracts = async () => {
    try {
      setLoading(true);
      const data = await contractsAPI.listContracts({
        status: statusFilter || undefined,
      });
      setContracts(data);
    } catch (error) {
      message.error('Failed to load contracts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setSelectedContract(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (record: ContractResponse) => {
    setSelectedContract(record);
    form.setFieldsValue({
      ...record,
      start_date: record.start_date ? dayjs(record.start_date) : null,
      end_date: record.end_date ? dayjs(record.end_date) : null,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await contractsAPI.deleteContract(id);
      message.success('Contract deleted successfully');
      loadContracts();
    } catch (error) {
      message.error('Failed to delete contract');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (selectedContract) {
        await contractsAPI.updateContract(selectedContract.id, values);
        message.success('Contract updated successfully');
      } else {
        await contractsAPI.createContract(values as ContractCreate);
        message.success('Contract created successfully');
      }
      setIsModalOpen(false);
      loadContracts();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save contract');
    }
  };

  const columns: ColumnsType<ContractResponse> = [
    {
      title: 'Contract #',
      dataIndex: 'contract_number',
      key: 'contract_number',
      width: 140,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value, record) =>
        record.title.toLowerCase().includes((value as string).toLowerCase()),
    },
    {
      title: 'Counterparty',
      dataIndex: 'counterparty_name',
      key: 'counterparty_name',
    },
    {
      title: 'Value',
      dataIndex: 'contract_value',
      key: 'contract_value',
      render: (value, record) =>
        value ? `${record.currency} ${parseFloat(value).toLocaleString()}` : '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status]}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleEdit(record)}
          >
            View
          </Button>
          <Popconfirm
            title="Delete contract?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>Contracts</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            New Contract
          </Button>
        </div>

        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search contracts..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 250 }}
          />
          <Select
            placeholder="Filter by status"
            style={{ width: 180 }}
            allowClear
            value={statusFilter || undefined}
            onChange={(value) => setStatusFilter(value || '')}
          >
            <Select.Option value="draft">Draft</Select.Option>
            <Select.Option value="pending_review">Pending Review</Select.Option>
            <Select.Option value="approved">Approved</Select.Option>
            <Select.Option value="signed">Signed</Select.Option>
            <Select.Option value="active">Active</Select.Option>
          </Select>
        </Space>

        <Table
          columns={columns}
          dataSource={contracts}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={selectedContract ? 'Contract Details' : 'New Contract'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="Title"
            name="title"
            rules={[{ required: true, message: 'Please enter contract title' }]}
          >
            <Input placeholder="Enter contract title" />
          </Form.Item>

          <Form.Item label="Description" name="description">
            <TextArea rows={3} placeholder="Contract description" />
          </Form.Item>

          <Form.Item
            label="Counterparty"
            name="counterparty_name"
            rules={[{ required: true, message: 'Please enter counterparty name' }]}
          >
            <Input placeholder="Company or individual name" />
          </Form.Item>

          <Form.Item label="Counterparty Contact" name="counterparty_contact">
            <Input placeholder="Email or phone" />
          </Form.Item>

          <Space style={{ width: '100%' }}>
            <Form.Item label="Contract Value" name="contract_value">
              <Input type="number" placeholder="0.00" />
            </Form.Item>
            <Form.Item label="Currency" name="currency" initialValue="USD">
              <Select style={{ width: 100 }}>
                <Select.Option value="USD">USD</Select.Option>
                <Select.Option value="EUR">EUR</Select.Option>
                <Select.Option value="GBP">GBP</Select.Option>
              </Select>
            </Form.Item>
          </Space>

          <Form.Item
            label="Content"
            name="content"
            rules={[{ required: true, message: 'Please enter contract content' }]}
          >
            <TextArea rows={6} placeholder="Contract terms and conditions..." />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {selectedContract ? 'Update' : 'Create'}
              </Button>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
