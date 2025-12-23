import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'destructive';
  onClick?: () => void;
}

const variants = {
  default: 'bg-card border-border/50',
  primary: 'bg-gradient-to-br from-primary/20 via-primary/10 to-transparent border-primary/50 shadow-glow-blue border-2',
  success: 'bg-gradient-to-br from-success/20 via-success/10 to-transparent border-success/50 shadow-glow-success border-2',
  warning: 'bg-gradient-to-br from-warning/20 via-warning/10 to-transparent border-warning/50 border-2',
  destructive: 'bg-gradient-to-br from-destructive/10 via-destructive/5 to-transparent border-destructive/30 border-2',
};

const iconVariants = {
  default: 'bg-muted text-muted-foreground',
  primary: 'bg-gradient-to-br from-primary to-primary/70 text-primary-foreground shadow-glow-blue animate-glow-pulse',
  success: 'bg-gradient-to-br from-success to-success/70 text-success-foreground shadow-glow-success animate-glow-pulse border border-success/30',
  warning: 'bg-gradient-to-br from-warning to-warning/70 text-warning-foreground animate-glow-pulse',
  destructive: 'bg-transparent text-destructive/70 border border-destructive/30',
};

export function StatCard({ title, value, icon: Icon, trend, variant = 'default', onClick }: StatCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'rounded-xl border p-6 shadow-card transition-all duration-300 hover:shadow-card-hover hover:scale-[1.02] animate-fade-in group relative overflow-hidden',
        variants[variant],
        variant === 'primary' && 'hover:border-primary/80',
        variant === 'success' && 'hover:border-success/80',
        variant === 'warning' && 'hover:border-warning/80',
        variant === 'destructive' && 'hover:border-destructive/50',
        onClick && 'cursor-pointer'
      )}
    >
      {/* Efeito shimmer */}
      <div className="absolute inset-0 animate-shimmer opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold text-foreground tracking-tight transition-colors">
            {value}
          </p>
          {trend && (
            <p
              className={cn(
                'text-sm font-semibold flex items-center gap-1',
                trend.isPositive ? 'text-success' : 'text-destructive'
              )}
            >
              <span className={cn(
                'inline-block w-0 h-0 border-l-[4px] border-r-[4px] border-b-[6px]',
                trend.isPositive 
                  ? 'border-b-success rotate-0' 
                  : 'border-b-destructive rotate-180'
              )} />
              {trend.isPositive ? '+' : '-'}
              {Math.abs(trend.value)}% este mês
            </p>
          )}
        </div>
        <div className={cn('p-3 rounded-xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 relative', iconVariants[variant])}>
          <Icon size={24} className="relative z-10" />
          {/* Efeito de brilho no ícone */}
          <div className={cn(
            'absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm',
            variant === 'primary' && 'bg-primary/50',
            variant === 'success' && 'bg-success/50',
            variant === 'warning' && 'bg-warning/50',
            variant === 'destructive' && 'bg-destructive/30'
          )} />
        </div>
      </div>
    </div>
  );
}
