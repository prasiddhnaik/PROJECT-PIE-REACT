import React from 'react';
import clsx from 'clsx';
import styles from './LoadingSpinner.module.css';

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'spin' | 'pulse' | 'bounce' | 'bars' | 'dots';
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'white';
}

const LoadingSpinner = React.forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  ({ className, size = 'md', variant = 'spin', color = 'primary', ...props }, ref) => {
    const sizes = {
      sm: styles.sm,
      md: styles.md,
      lg: styles.lg,
      xl: styles.xl
    };

    const colors = {
      primary: styles.primary,
      secondary: styles.secondary,
      success: styles.success,
      error: styles.error,
      warning: styles.warning,
      white: styles.white
    };

    if (variant === 'spin') {
      return (
        <div
          ref={ref}
          className={clsx(
            styles.spinner,
            styles.spin,
            sizes[size],
            colors[color],
            className
          )}
          {...props}
        />
      );
    }

    if (variant === 'dots') {
      return (
        <div
          ref={ref}
          className={clsx(
            styles.spinner,
            styles.dots,
            sizes[size],
            colors[color],
            className
          )}
          {...props}
        >
          <div className={styles.dot} />
          <div className={styles.dot} />
          <div className={styles.dot} />
        </div>
      );
    }

    if (variant === 'pulse') {
      return (
        <div
          ref={ref}
          className={clsx(
            styles.spinner,
            styles.pulse,
            sizes[size],
            colors[color],
            className
          )}
          {...props}
        />
      );
    }

    if (variant === 'bars') {
      return (
        <div
          ref={ref}
          className={clsx(
            styles.spinner,
            styles.bars,
            sizes[size],
            colors[color],
            className
          )}
          {...props}
        >
          <div className={styles.bar} />
          <div className={styles.bar} />
          <div className={styles.bar} />
        </div>
      );
    }

    if (variant === 'bounce') {
      return (
        <div
          ref={ref}
          className={clsx(
            styles.spinner,
            styles.bounce,
            sizes[size],
            colors[color],
            className
          )}
          {...props}
        />
      );
    }

    return null;
  }
);

LoadingSpinner.displayName = 'LoadingSpinner';

export { LoadingSpinner }; 