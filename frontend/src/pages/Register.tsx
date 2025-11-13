/**
 * Registration Page
 */
import { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Space, Select } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../contexts/AuthContext';
import { UserRole } from '../types/api';
import type { UserCreate } from '../types/api';

const { Title, Text } = Typography;
const { Option } = Select;

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const onFinish = async (values: UserCreate) => {
    try {
      setIsLoading(true);
      clearError();
      await register(values);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      // Error handled in store
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card style={{ width: 450, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>Create Account</Title>
            <Text type="secondary">Join Contract Management System</Text>
          </div>

          {error && (
            <Alert
              message="Registration Failed"
              description={error}
              type="error"
              closable
              onClose={clearError}
            />
          )}

          <Form
            name="register"
            onFinish={onFinish}
            autoComplete="off"
            layout="vertical"
            initialValues={{ role: UserRole.PROCUREMENT }}
          >
            <Form.Item
              label="Full Name"
              name="full_name"
              rules={[{ required: true, message: 'Please input your full name!' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="John Doe" />
            </Form.Item>

            <Form.Item
              label="Email"
              name="email"
              rules={[
                { required: true, message: 'Please input your email!' },
                { type: 'email', message: 'Please enter a valid email!' },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="john@example.com" />
            </Form.Item>

            <Form.Item
              label="Role"
              name="role"
              rules={[{ required: true, message: 'Please select a role!' }]}
            >
              <Select>
                <Option value={UserRole.PROCUREMENT}>Procurement</Option>
                <Option value={UserRole.LEGAL}>Legal</Option>
                <Option value={UserRole.FINANCE}>Finance</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="Password"
              name="password"
              rules={[
                { required: true, message: 'Please input your password!' },
                { min: 8, message: 'Password must be at least 8 characters!' },
                {
                  pattern: /^(?=.*[A-Za-z])(?=.*\d)/,
                  message: 'Password must contain letters and numbers!',
                },
              ]}
              hasFeedback
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Min. 8 characters" />
            </Form.Item>

            <Form.Item
              label="Confirm Password"
              name="confirm_password"
              dependencies={['password']}
              hasFeedback
              rules={[
                { required: true, message: 'Please confirm your password!' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Passwords do not match!'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Confirm password" />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={isLoading}
                block
                size="large"
              >
                Register
              </Button>
            </Form.Item>

            <div style={{ textAlign: 'center' }}>
              <Text>
                Already have an account?{' '}
                <Link to="/login">Sign in</Link>
              </Text>
            </div>
          </Form>
        </Space>
      </Card>
    </div>
  );
};
