// QuickStartCards component
import React from 'react';
import { TrendingUp, Sparkles, Award } from 'lucide-react';
import { QUICK_START_OPTIONS } from '../utils/constants';

const QuickStartCards = ({ onQuickSearch }) => {
  const cardConfigs = [
    {
      ...QUICK_START_OPTIONS[0],
      icon: TrendingUp,
      gradient: 'from-blue-50 to-indigo-100',
      border: 'border-blue-200',
      iconColor: 'text-blue-600'
    },
    {
      ...QUICK_START_OPTIONS[1],
      icon: Sparkles,
      gradient: 'from-pink-50 to-rose-100',
      border: 'border-pink-200',
      iconColor: 'text-pink-600'
    },
    {
      ...QUICK_START_OPTIONS[2],
      icon: Award,
      gradient: 'from-purple-50 to-violet-100',
      border: 'border-purple-200',
      iconColor: 'text-purple-600'
    }
  ];

  return (
    <div className="grid md:grid-cols-3 gap-6 mb-8">
      {cardConfigs.map((option) => {
        const IconComponent = option.icon;
        return (
          <div 
            key={option.id}
            className={`bg-gradient-to-br ${option.gradient} p-6 rounded-xl border ${option.border} cursor-pointer hover:shadow-lg transition-shadow`}
            onClick={() => onQuickSearch(option.query)}
          >
            <IconComponent className={`h-8 w-8 ${option.iconColor} mb-3`} />
            <h3 className="font-semibold text-gray-900 mb-2">{option.title}</h3>
            <p className="text-sm text-gray-600">{option.description}</p>
          </div>
        );
      })}
    </div>
  );
};

export default QuickStartCards;