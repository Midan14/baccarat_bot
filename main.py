#!/usr/bin/env python3
"""
Punto de entrada principal para el Baccarat Bot Avanzado
"""

import sys
import asyncio
import argparse
import os
from pathlib import Path
import logging

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import BotConfig, setup_logger
from bot_avanzado_completo import AdvancedBaccaratBot
from bot_senales_telegram import TelegramSignalsBot

# Configurar logging
logger = setup_logger('main')

def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Baccarat Bot Avanzado - Sistema de predicción con IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py --mode full           # Ejecutar bot completo
  python main.py --mode signals        # Solo señales de Telegram
  python main.py --config custom.json  # Usar configuración personalizada
  python main.py --demo               # Modo demo sin apuestas reales
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'signals', 'demo'],
        default='full',
        help='Modo de operación del bot'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Archivo de configuración JSON'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Ejecutar en modo demo (sin apuestas reales)'
    )
    
    parser.add_argument(
        '--bankroll',
        type=float,
        help='Bankroll inicial para modo demo'
    )
    
    parser.add_argument(
        '--telegram-token',
        type=str,
        help='Token del bot de Telegram'
    )
    
    parser.add_argument(
        '--telegram-chat',
        type=str,
        help='Chat ID de Telegram'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Nivel de logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Baccarat Bot Avanzado v2.0'
    )
    
    return parser.parse_args()

async def load_configuration(args):
    """Carga la configuración según los argumentos"""
    
    # Crear configuración base
    config = BotConfig()
    
    # Cargar desde archivo si se especifica
    if args.config:
        try:
            config = BotConfig.load_from_file(args.config)
            logger.info(f"Configuración cargada desde: {args.config}")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            sys.exit(1)
    
    # Aplicar argumentos de línea de comandos
    if args.demo:
        config.signals.confirm_bets = False
        logger.info("Modo demo activado - No se realizarán apuestas reales")
    
    if args.bankroll:
        config.bankroll.initial_amount = args.bankroll
        logger.info(f"Bankroll inicial: ${args.bankroll}")
    
    if args.telegram_token:
        config.telegram.bot_token = args.telegram_token
    
    if args.telegram_chat:
        config.telegram.chat_id = args.telegram_chat
    
    # Validar configuración mínima
    if not config.telegram.bot_token or not config.telegram.chat_id:
        logger.warning("No se configuró Telegram. Las señales se mostrarán solo en consola.")
        config.telegram.enabled = False
    
    if not config.data_sources:
        logger.warning("No se configuraron fuentes de datos. Usando modo demo.")
    
    return config

async def run_full_bot(config):
    """Ejecuta el bot completo"""
    logger.info("🚀 Iniciando Baccarat Bot Avanzado (Modo Completo)")
    
    try:
        # Convertir BotConfig a diccionario para AdvancedBaccaratBot
        config_dict = config.to_dict() if hasattr(config, 'to_dict') else config
        bot = AdvancedBaccaratBot(config_dict)
        await bot.initialize()
        await bot.start()
        
    except Exception as e:
        logger.error(f"Error en bot completo: {e}")
        raise

async def run_signals_bot(config):
    """Ejecuta solo el bot de señales"""
    logger.info("📱 Iniciando Bot de Señales Telegram")
    
    try:
        # TelegramSignalsBot espera un diccionario de configuración
        bot = TelegramSignalsBot(config.to_dict() if hasattr(config, 'to_dict') else config)
        await bot.initialize()
        await bot.start()
        
    except Exception as e:
        logger.error(f"Error en bot de señales: {e}")
        raise

async def run_demo_mode(config):
    """Ejecuta en modo demo"""
    logger.info("🎮 Iniciando en Modo Demo")
    
    # Configurar para modo demo
    config.signals.confirm_bets = False
    config.monte_carlo.num_simulations = 1000  # Menos simulaciones para demo
    
    # Usar bot de señales para demo
    await run_signals_bot(config)

async def main():
    """Función principal"""
    
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Configurar logging
        if args.log_level:
            os.environ['LOG_LEVEL'] = args.log_level
        
        logger.info("🎲 Baccarat Bot Avanzado v2.0")
        logger.info("=" * 50)
        
        # Cargar configuración
        config = await load_configuration(args)
        
        # Mostrar configuración
        logger.info("Configuración cargada:")
        logger.info(f"  • Modo: {args.mode}")
        logger.info(f"  • Bankroll: ${config.bankroll.initial_amount}")
        logger.info(f"  • Telegram: {'✅' if config.telegram.enabled else '❌'}")
        logger.info(f"  • Fuentes de datos: {len(config.data_sources)}")
        logger.info(f"  • Simulaciones Monte Carlo: {config.monte_carlo.num_simulations:,}")
        
        # Ejecutar según el modo
        if args.mode == 'full':
            await run_full_bot(config)
        elif args.mode == 'signals':
            await run_signals_bot(config)
        elif args.mode == 'demo':
            await run_demo_mode(config)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar aplicación
    asyncio.run(main())