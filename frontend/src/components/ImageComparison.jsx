import React from 'react';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { GitCompareArrows } from 'lucide-react';

/**
 * Before/after image comparison using react-compare-slider.
 */
export default function ImageComparison({ originalBase64, adversarialBase64 }) {
    if (!originalBase64 || !adversarialBase64) {
        return (
            <div className="card">
                <div className="card-header">
                    <div className="card-title">
                        <GitCompareArrows size={14} className="card-title-icon" />
                        Image Comparison
                    </div>
                </div>
                <div className="empty-state" style={{ padding: 20 }}>
                    <span className="empty-state-text">Run an attack to compare images</span>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-title">
                    <GitCompareArrows size={14} className="card-title-icon" />
                    Image Comparison
                </div>
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Drag slider to compare</span>
            </div>
            <div style={{ borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
                <ReactCompareSlider
                    itemOne={
                        <ReactCompareSliderImage
                            src={`data:image/png;base64,${originalBase64}`}
                            alt="Original"
                            style={{ imageRendering: 'pixelated' }}
                        />
                    }
                    itemTwo={
                        <ReactCompareSliderImage
                            src={`data:image/png;base64,${adversarialBase64}`}
                            alt="Adversarial"
                            style={{ imageRendering: 'pixelated' }}
                        />
                    }
                    style={{ height: 250 }}
                />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                <span>Original</span>
                <span>Adversarial</span>
            </div>
        </div>
    );
}
