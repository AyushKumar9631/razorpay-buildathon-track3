import React from 'react';
import Link from 'next/link';
import { Home, AlertTriangle, Zap, BarChart3, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Risks', href: '/risks', icon: AlertTriangle },
  { name: 'Interventions', href: '/interventions', icon: Zap },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Audit Trail', href: '/audit', icon: FileText },
];

export default function Sidebar() {
  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="flex flex-col flex-grow pt-5 bg-gray-900 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <h1 className="text-xl font-bold text-white">
            AI Revenue Recovery
          </h1>
        </div>
        <div className="mt-8 flex-1 flex flex-col">
          <nav className="flex-1 px-2 pb-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                    'text-gray-300 hover:bg-gray-800 hover:text-white transition-colors'
                  )}
                >
                  <Icon className="mr-3 flex-shrink-0 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex-shrink-0 flex border-t border-gray-800 p-4">
          <div className="flex items-center">
            <div>
              <p className="text-sm font-medium text-white">Demo Mode</p>
              <p className="text-xs text-gray-400">Razorpay Buildathon 2026</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
