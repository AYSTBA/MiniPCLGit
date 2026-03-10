from flask import Blueprint, jsonify, request
from services import (
    find_all_minecraft_folders,
    get_version_list,
    get_save_info,
    do_full_backup,
    do_restore_zip,
    get_backup_history,
    delete_backup
)

api_bp = Blueprint('api', __name__)

@api_bp.route('/minecraft/folders', methods=['GET'])
def get_minecraft_folders():
    try:
        folders = find_all_minecraft_folders()
        return jsonify({'success': True, 'data': folders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/minecraft/versions', methods=['GET'])
def get_versions():
    try:
        mc_root = request.args.get('mc_root')
        if not mc_root:
            return jsonify({'success': False, 'error': 'mc_root is required'})
        versions = get_version_list(mc_root)
        return jsonify({'success': True, 'data': versions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/minecraft/saves', methods=['GET'])
def get_saves():
    try:
        mc_root = request.args.get('mc_root')
        version = request.args.get('version')
        if not mc_root or not version:
            return jsonify({'success': False, 'error': 'mc_root and version are required'})
        saves, save_root, save_type = get_save_info(mc_root, version)
        return jsonify({'success': True, 'data': {'saves': saves, 'save_root': save_root, 'save_type': save_type}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/backup', methods=['POST'])
def create_backup():
    try:
        data = request.json
        mc_root = data.get('mc_root')
        save_root = data.get('save_root')
        selected_items = data.get('selected_items')
        selected_save = data.get('selected_save')
        note = data.get('note', '')
        
        if not mc_root or not save_root or not selected_items or not selected_save:
            return jsonify({'success': False, 'error': 'Missing required parameters'})
        
        success, failed = do_full_backup(mc_root, save_root, selected_items, selected_save, note)
        return jsonify({'success': True, 'data': {'success': success, 'failed': failed}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/restore', methods=['POST'])
def restore_backup():
    try:
        data = request.json
        zip_path = data.get('zip_path')
        target_mc_root = data.get('target_mc_root')
        save_root = data.get('save_root')
        
        if not zip_path or not target_mc_root or not save_root:
            return jsonify({'success': False, 'error': 'Missing required parameters'})
        
        do_restore_zip(zip_path, target_mc_root, save_root)
        return jsonify({'success': True, 'message': 'Restore completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/backup/history', methods=['GET'])
def get_backup_history_endpoint():
    try:
        version = request.args.get('version')
        save_name = request.args.get('save_name')
        
        if not version or not save_name:
            return jsonify({'success': False, 'error': 'version and save_name are required'})
        
        history = get_backup_history(version, save_name)
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@api_bp.route('/backup/delete', methods=['POST'])
def delete_backup_endpoint():
    try:
        data = request.json
        backup_path = data.get('backup_path')
        
        if not backup_path:
            return jsonify({'success': False, 'error': 'backup_path is required'})
        
        delete_backup(backup_path)
        return jsonify({'success': True, 'message': 'Backup deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})