"""Eval results viewer components for the Streamlit app."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from config import get_eval_file_path
from utils.logging import get_logger, log_exception

# Setup logger
logger = get_logger(__name__)


def load_eval_results(file_path: Optional[Path] = None) -> Optional[List[Dict[str, Any]]]:
    """Load eval results from JSON file.

    Args:
        file_path: Optional specific file path, otherwise uses config

    Returns:
        List of eval results or None if loading fails

    """
    try:
        if file_path is None:
            file_path = get_eval_file_path()

        if file_path is None:
            logger.warning("No eval results file found")
            return None

        if not file_path.exists():
            logger.warning(f"Eval results file does not exist: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

        logger.info(f"Loaded {len(results)} eval results from {file_path}")
        return results

    except Exception as e:
        log_exception(logger, e, f"loading eval results from {file_path}")
        return None


def calculate_summary_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics from eval results.

    Args:
        results: List of eval result dictionaries

    Returns:
        Dictionary with summary statistics

    """
    try:
        if not results:
            return {}

        # Extract scores - handle both old and new format
        overall_scores = []
        factual_scores = []
        completeness_scores = []
        relevance_scores = []
        usefulness_scores = []
        
        for r in results:
            # Handle overall score
            if 'overall_score' in r:
                overall_scores.append(r['overall_score'])
            
            # Handle nested grade structure or flat structure
            if 'grade' in r and isinstance(r['grade'], dict):
                # New format with nested grades
                grade = r['grade']
                if 'accuracy' in grade:
                    factual_scores.append(grade['accuracy'])
                if 'completeness' in grade:
                    completeness_scores.append(grade['completeness'])
                if 'relevance' in grade:
                    relevance_scores.append(grade['relevance'])
                # Handle both 'clarity' and 'usefulness' as equivalent
                if 'clarity' in grade:
                    usefulness_scores.append(grade['clarity'])
                elif 'usefulness' in grade:
                    usefulness_scores.append(grade['usefulness'])
            else:
                # Old flat format
                if 'factual_accuracy' in r:
                    factual_scores.append(r['factual_accuracy'])
                if 'completeness' in r:
                    completeness_scores.append(r['completeness'])
                if 'relevance' in r:
                    relevance_scores.append(r['relevance'])
                if 'usefulness' in r:
                    usefulness_scores.append(r['usefulness'])
        
        # Dataset breakdown - handle both 'dataset' and 'expected_dataset'
        datasets = {}
        for result in results:
            dataset = result.get('dataset') or result.get('expected_dataset', 'Unknown')
            if dataset not in datasets:
                datasets[dataset] = {'total': 0, 'scores': []}
            datasets[dataset]['total'] += 1
            if 'overall_score' in result:
                datasets[dataset]['scores'].append(result['overall_score'])

        # Calculate averages
        stats = {
            'total_questions': len(results),
            'overall_score_avg': sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            'overall_score_min': min(overall_scores) if overall_scores else 0,
            'overall_score_max': max(overall_scores) if overall_scores else 0,
            'factual_accuracy_avg': sum(factual_scores) / len(factual_scores) if factual_scores else 0,
            'completeness_avg': sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0,
            'relevance_avg': sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            'usefulness_avg': sum(usefulness_scores) / len(usefulness_scores) if usefulness_scores else 0,
            'datasets': datasets,
            'timestamp': results[0].get('timestamp', '') if results else ''
        }

        logger.debug("Summary statistics calculated successfully")
        return stats

    except Exception as e:
        log_exception(logger, e, "calculating summary statistics")
        return {}


def render_summary_metrics(stats: Dict[str, Any]) -> None:
    """Render summary metrics cards.

    Args:
        stats: Summary statistics dictionary

    """
    try:
        st.subheader("📈 Přehled výsledků")
        
        # Create columns for metrics (removed success rate)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Celkové skóre",
                value=f"{stats.get('overall_score_avg', 0):.1f}/5.0",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Počet otázek",
                value=f"{stats.get('total_questions', 0)}",
                delta=None
            )
        
        with col3:
            # Extract date from timestamp if available
            timestamp = stats.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d.%m.%Y')
                except:
                    date_str = timestamp[:10] if len(timestamp) >= 10 else timestamp
            else:
                date_str = "Neznámé"
            
            st.metric(
                label="Datum vyhodnocení",
                value=date_str,
                delta=None
            )

    except Exception as e:
        log_exception(logger, e, "rendering summary metrics")
        st.error("Chyba při zobrazování souhrnných metrik")


def render_detailed_metrics(stats: Dict[str, Any]) -> None:
    """Render detailed metrics breakdown.

    Args:
        stats: Summary statistics dictionary

    """
    try:
        st.subheader("📊 Detailní metriky")
        
        # Metrics breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Průměrné skóre podle kategorií:**")
            metrics_data = {
                'Kategorie': ['Faktická správnost', 'Úplnost', 'Relevance', 'Užitečnost'],
                'Průměrné skóre': [
                    stats.get('factual_accuracy_avg', 0),
                    stats.get('completeness_avg', 0),
                    stats.get('relevance_avg', 0),
                    stats.get('usefulness_avg', 0)
                ]
            }
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, hide_index=True)
        
        with col2:
            st.write("**Výsledky podle datových sad:**")
            datasets = stats.get('datasets', {})
            if datasets:
                dataset_data = {
                    'Dataset': [],
                    'Počet otázek': [],
                    'Průměrné skóre': []
                }
                for dataset, data in datasets.items():
                    dataset_data['Dataset'].append(dataset)
                    dataset_data['Počet otázek'].append(data['total'])
                    avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                    dataset_data['Průměrné skóre'].append(f"{avg_score:.1f}")
                
                dataset_df = pd.DataFrame(dataset_data)
                st.dataframe(dataset_df, hide_index=True)

    except Exception as e:
        log_exception(logger, e, "rendering detailed metrics")
        st.error("Chyba při zobrazování detailních metrik")


def render_results_table(results: List[Dict[str, Any]]) -> None:
    """Render detailed results table.

    Args:
        results: List of eval result dictionaries

    """
    try:
        st.subheader("📋 Detailní výsledky")
        
        # Prepare data for table
        table_data = []
        for i, result in enumerate(results, 1):
            # Handle different field formats
            dataset = result.get('dataset') or result.get('expected_dataset', 'N/A')
            
            # Extract individual scores from nested or flat structure
            if 'grade' in result and isinstance(result['grade'], dict):
                # New nested format
                grade = result['grade']
                factual_score = grade.get('accuracy', 0)
                completeness_score = grade.get('completeness', 0)
                relevance_score = grade.get('relevance', 0)
                usefulness_score = grade.get('clarity', grade.get('usefulness', 0))
            else:
                # Old flat format
                factual_score = result.get('factual_accuracy', 0)
                completeness_score = result.get('completeness', 0)
                relevance_score = result.get('relevance', 0)
                usefulness_score = result.get('usefulness', 0)
            
            table_data.append({
                '#': i,
                'Otázka': result.get('question', '')[:100] + ('...' if len(result.get('question', '')) > 100 else ''),
                'Dataset': dataset,
                'Celkové skóre': f"{result.get('overall_score', 0):.1f}/5",
                'Faktická správnost': f"{factual_score:.1f}",
                'Úplnost': f"{completeness_score:.1f}",
                'Relevance': f"{relevance_score:.1f}",
                'Užitečnost': f"{usefulness_score:.1f}"
            })
        
        # Display table
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Expandable sections for detailed view
        st.subheader("🔍 Detailní pohled na jednotlivé otázky")
        
        for i, result in enumerate(results, 1):
            with st.expander(f"Otázka {i}: {result.get('question', '')[:80]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Otázka:**")
                    st.write(result.get('question', 'N/A'))
                    
                    st.write("**Správná odpověď:**")
                    st.write(result.get('ground_truth', 'N/A'))
                
                with col2:
                    st.write("**Odpověď agenta:**")
                    st.write(result.get('response', 'N/A'))
                    
                    # Handle both flat and nested reasoning
                    reasoning = result.get('justification') or result.get('grading_reasoning')
                    if 'grade' in result and isinstance(result['grade'], dict):
                        reasoning = reasoning or result['grade'].get('reasoning')
                    
                    st.write("**Zdůvodnění:**")
                    st.write(reasoning or 'N/A')

    except Exception as e:
        log_exception(logger, e, "rendering results table")
        st.error("Chyba při zobrazování tabulky výsledků")


def render_eval_dashboard() -> None:
    """Render the complete eval results dashboard."""
    try:
        st.title("📊 Výsledky vyhodnocení agenta")
        
        # Load eval results
        results = load_eval_results()
        
        if results is None:
            st.warning("⚠️ Nepodařilo se načíst výsledky vyhodnocení.")
            st.info("Zkontrolujte, zda existují soubory s výsledky v složce `eval/results/grades/`")
            return
        
        if not results:
            st.warning("⚠️ Nebyli nalezeni žádné výsledky vyhodnocení.")
            return
        
        # Calculate summary statistics
        stats = calculate_summary_stats(results)
        
        if not stats:
            st.error("❌ Chyba při výpočtu statistik")
            return
        
        # Render dashboard components
        render_summary_metrics(stats)
        st.divider()
        render_detailed_metrics(stats)
        st.divider()
        render_results_table(results)
        
        # Display file info
        file_path = get_eval_file_path()
        if file_path:
            st.info(f"📁 Načteno ze souboru: `{file_path.name}`")

    except Exception as e:
        log_exception(logger, e, "rendering eval dashboard")
        st.error("❌ Došlo k chybě při zobrazování dashboard") 