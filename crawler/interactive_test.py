#!/usr/bin/env python3
"""Script interactivo para probar el Enhanced Crawler con IA."""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

try:
    from core_enhanced import EnhancedCrawler
    print("✓ Módulo core_enhanced importado correctamente\n")
except ImportError as e:
    print(f"✗ Error al importar core_enhanced: {e}")
    sys.exit(1)


def print_header(title: str):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_response(result: dict):
    """Imprime una respuesta formateada."""
    response = result['response']
    
    print(f"\n📝 PREGUNTA:")
    print(f"   {result['prompt']}")
    
    print(f"\n🎯 ANÁLISIS:")
    print(f"   • Intención: {response.get('intent', 'N/A')}")
    print(f"   • Tipo: {response.get('question_type', 'N/A')}")
    print(f"   • Complejidad: {response.get('complexity', 'N/A')}")
    print(f"   • Estilo: {response.get('style', 'N/A')}")
    
    print(f"\n🤖 SISTEMA:")
    print(f"   • Proveedor IA: {response.get('ai_provider', 'N/A')}")
    print(f"   • Confianza: {response.get('confidence', 0):.0%}")
    print(f"   • Fuentes: {len(response.get('sources', []))}")
    
    keywords = response.get('keywords', [])[:5]
    if keywords:
        print(f"   • Keywords: {', '.join(keywords)}")
    
    print(f"\n💬 RESPUESTA:")
    print("-" * 70)
    print(response.get('response_text', 'Sin respuesta'))
    print("-" * 70)
    
    sources = response.get('sources', [])
    if sources:
        print(f"\n📚 FUENTES ({len(sources)}):")
        for i, source in enumerate(sources[:5], 1):
            print(f"   {i}. {source}")
        if len(sources) > 5:
            print(f"   ... y {len(sources) - 5} más")
    
    stats = response.get('learning_stats', {})
    if stats:
        print(f"\n📊 ESTADÍSTICAS DE APRENDIZAJE:")
        print(f"   • Total feedback: {stats.get('total_feedback', 0)}")
        print(f"   • Feedback positivo: {stats.get('positive_feedback', 0)}")
        print(f"   • Temas aprendidos: {stats.get('learned_topics', 0)}")
        print(f"   • Hechos aprendidos: {stats.get('learned_facts', 0)}")


def test_system_info(crawler):
    """Muestra información del sistema."""
    print_header("INFORMACIÓN DEL SISTEMA")
    
    ai_provider = "No disponible"
    if crawler.ai_provider and crawler.ai_provider.provider:
        ai_provider = crawler.ai_provider.provider.upper()
    
    print(f"\n✓ Sistema Enhanced Crawler v3.0")
    print(f"\n🧠 IA Generativa:")
    print(f"   • Proveedor: {ai_provider}")
    
    if ai_provider == "No disponible":
        print(f"   ⚠️  Sin IA configurada - usando fallback")
        print(f"   💡 Para habilitar IA:")
        print(f"      1. Instala: pip install anthropic (o openai)")
        print(f"      2. Configura ANTHROPIC_API_KEY en .env")
    
    print(f"\n💾 Caché:")
    print(f"   • Estado: {'Activado' if crawler.fetcher.cache else 'Desactivado'}")
    
    print(f"\n🎓 Aprendizaje:")
    stats = crawler.learning.get_learning_stats()
    print(f"   • Total feedback: {stats.get('total_feedback', 0)}")
    print(f"   • Temas aprendidos: {stats.get('learned_topics', 0)}")


def test_predefined_queries(crawler):
    """Prueba consultas predefinidas."""
    print_header("PRUEBAS PREDEFINIDAS")
    
    queries = [
        "¿Qué es Python?",
        "¿Cómo funciona machine learning?",
        "Diferencias entre Python y JavaScript",
        "¿Por qué es importante la inteligencia artificial?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n\n{'─' * 70}")
        print(f"PRUEBA {i}/{len(queries)}")
        print('─' * 70)
        
        try:
            result = crawler.run(query)
            print_response(result)
            
            # Simular feedback automático
            confidence = result['response'].get('confidence', 0)
            useful = confidence > 0.5
            
            print(f"\n🔄 Feedback automático: {'✓ Útil' if useful else '✗ No útil'}")
            crawler.add_feedback(query, result['response'], useful)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
        
        if i < len(queries):
            input("\nPresiona Enter para continuar...")


def interactive_mode(crawler):
    """Modo interactivo."""
    print_header("MODO INTERACTIVO")
    
    print("\n🎮 Comandos disponibles:")
    print("   • Escribe tu pregunta para hacer una consulta")
    print("   • 'stats' - Ver estadísticas")
    print("   • 'clear' - Limpiar pantalla")
    print("   • 'exit' o 'quit' - Salir")
    print("\nComenzamos! 🚀\n")
    
    while True:
        try:
            prompt = input("\n💭 Tu pregunta: ").strip()
            
            if not prompt:
                continue
            
            if prompt.lower() in ['exit', 'quit', 'salir']:
                print("\n👋 ¡Hasta luego!")
                break
            
            if prompt.lower() == 'stats':
                stats = crawler.learning.get_learning_stats()
                print("\n📊 ESTADÍSTICAS:")
                print(f"   • Total feedback: {stats.get('total_feedback', 0)}")
                print(f"   • Feedback positivo: {stats.get('positive_feedback', 0)}")
                print(f"   • Temas aprendidos: {stats.get('learned_topics', 0)}")
                print(f"   • Hechos aprendidos: {stats.get('learned_facts', 0)}")
                continue
            
            if prompt.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
            
            # Procesar consulta
            print("\n⏳ Procesando...")
            result = crawler.run(prompt)
            print_response(result)
            
            # Pedir feedback
            feedback = input("\n¿Fue útil esta respuesta? (s/n): ").strip().lower()
            
            if feedback in ['s', 'si', 'sí', 'y', 'yes']:
                crawler.add_feedback(prompt, result['response'], True)
                print("✓ Gracias! El sistema ha aprendido de tu feedback positivo")
            elif feedback in ['n', 'no']:
                crawler.add_feedback(prompt, result['response'], False)
                print("✓ Gracias! Trabajaremos en mejorar")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")


def main():
    """Función principal."""
    print("\n" + "🤖" * 35)
    print("  ENHANCED CRAWLER - SISTEMA INTERACTIVO DE PRUEBAS")
    print("🤖" * 35)
    
    # Crear instancia del crawler
    print("\n⏳ Inicializando sistema...")
    
    use_cache = os.getenv('USE_CACHE', 'true').lower() == 'true'
    crawler = EnhancedCrawler(use_cache=use_cache, use_ai=True)
    
    print("✓ Sistema inicializado correctamente")
    
    # Mostrar información del sistema
    test_system_info(crawler)
    
    # Menú principal
    while True:
        print_header("MENÚ PRINCIPAL")
        print("\n1. Ver información del sistema")
        print("2. Ejecutar pruebas predefinidas")
        print("3. Modo interactivo (hacer tus propias preguntas)")
        print("4. Salir")
        
        choice = input("\nElige una opción (1-4): ").strip()
        
        if choice == '1':
            test_system_info(crawler)
        elif choice == '2':
            test_predefined_queries(crawler)
        elif choice == '3':
            interactive_mode(crawler)
        elif choice == '4':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Por favor elige 1-4.")
    
    # Mostrar estadísticas finales
    print_header("ESTADÍSTICAS FINALES")
    stats = crawler.learning.get_learning_stats()
    print(f"\n📊 Durante esta sesión:")
    print(f"   • Total de feedback: {stats.get('total_feedback', 0)}")
    print(f"   • Feedback positivo: {stats.get('positive_feedback', 0)}")
    print(f"   • Temas aprendidos: {stats.get('learned_topics', 0)}")
    print(f"   • Hechos aprendidos: {stats.get('learned_facts', 0)}")
    
    print("\n✨ Gracias por usar Enhanced Crawler!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)