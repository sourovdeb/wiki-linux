<?php
/**
 * Plugin Name: WordPress Control Prototype
 * Description: Safe, local-first WordPress control bridge for VS Code automation.
 * Version: 3.0.0-prototype
 * Author: Sourov Deb
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'WPC_VERSION', '3.0.0-prototype' );
define( 'WPC_NS', 'sourov/v2' );
define( 'WPC_AUDIT_OPTION', 'wpc_audit_log' );
define( 'WPC_ALLOWED_CATEGORIES_OPTION', 'wpc_allowed_categories' );
define( 'WPC_PLUGIN_KEY_OPTION', 'wpc_plugin_key' );

add_action( 'rest_api_init', 'wpc_register_routes' );

function wpc_register_routes() {
	register_rest_route(
		WPC_NS,
		'/health',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_health',
				'permission_callback' => '__return_true',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/info',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_info',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_list_posts',
				'permission_callback' => 'wpc_permission_allow',
				'args'                => array(
					'status'   => array(
						'type'              => 'string',
						'sanitize_callback' => 'sanitize_text_field',
					),
					'page'     => array(
						'type'              => 'integer',
						'default'           => 1,
						'sanitize_callback' => 'absint',
					),
					'per_page' => array(
						'type'              => 'integer',
						'default'           => 20,
						'sanitize_callback' => 'absint',
					),
					'search'   => array(
						'type'              => 'string',
						'sanitize_callback' => 'sanitize_text_field',
					),
				),
			),
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_create_post',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts/bulk',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_bulk_create_posts',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts/(?P<id>[\d]+)',
		array(
			'args' => array(
				'id' => array(
					'type'              => 'integer',
					'sanitize_callback' => 'absint',
				),
			),
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_get_post',
				'permission_callback' => 'wpc_permission_allow',
			),
			array(
				'methods'             => 'PATCH',
				'callback'            => 'wpc_patch_post',
				'permission_callback' => 'wpc_permission_allow',
			),
			array(
				'methods'             => WP_REST_Server::DELETABLE,
				'callback'            => 'wpc_delete_post',
				'permission_callback' => 'wpc_permission_allow',
				'args'                => array(
					'force' => array(
						'type'              => 'boolean',
						'default'           => false,
						'sanitize_callback' => 'rest_sanitize_boolean',
					),
				),
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts/(?P<id>[\d]+)/publish',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_publish_post',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts/(?P<id>[\d]+)/schedule',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_schedule_post',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/posts/(?P<id>[\d]+)/unschedule',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_unschedule_post',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/categories',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_list_categories',
				'permission_callback' => 'wpc_permission_allow',
			),
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'wpc_create_category',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/audit-log',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_get_audit_log',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);

	register_rest_route(
		WPC_NS,
		'/templates/(?P<name>[a-z0-9\-]+)',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'wpc_get_template',
				'permission_callback' => 'wpc_permission_allow',
			),
		)
	);
}

function wpc_permission_allow() {
	return true;
}

function wpc_request_id() {
	return 'req_' . wp_generate_uuid4();
}

function wpc_success( $payload, $status = 200 ) {
	$data = array(
		'api_version' => WPC_VERSION,
		'request_id'  => wpc_request_id(),
	);

	if ( is_array( $payload ) ) {
		$data = array_merge( $data, $payload );
	} else {
		$data['value'] = $payload;
	}

	return new WP_REST_Response( $data, $status );
}

function wpc_error( $status, $code, $message, $target = '', $details = array() ) {
	$err = array(
		'error' => array(
			'code'       => $code,
			'message'    => $message,
			'target'     => $target,
			'details'    => $details,
			'request_id' => wpc_request_id(),
		),
	);

	$response = new WP_REST_Response( $err, $status );
	if ( 429 === (int) $status ) {
		$response->header( 'Retry-After', '60' );
	}

	return $response;
}

function wpc_guard_private( $request ) {
	$rate = wpc_rate_limit_check();
	if ( true !== $rate ) {
		return $rate;
	}

	if ( current_user_can( 'edit_posts' ) ) {
		return true;
	}

	$configured_key = (string) get_option( WPC_PLUGIN_KEY_OPTION, '' );
	$incoming_key   = (string) $request->get_header( 'x-sourov-key' );

	if ( '' !== $configured_key && '' !== $incoming_key && hash_equals( $configured_key, $incoming_key ) ) {
		return true;
	}

	return wpc_error( 403, 'forbidden', 'You are not allowed to perform this action.', 'authorization' );
}

function wpc_rate_limit_check() {
	$ip        = (string) ( $_SERVER['REMOTE_ADDR'] ?? 'unknown' );
	$cache_key = 'wpc_rl_' . md5( $ip );
	$count     = (int) get_transient( $cache_key );

	if ( $count >= 60 ) {
		return wpc_error(
			429,
			'tooManyRequests',
			'Request limit exceeded for this IP. Retry after one minute.',
			'rate_limit',
			array(
				'limit' => 60,
				'ip'    => $ip,
			)
		);
	}

	set_transient( $cache_key, $count + 1, MINUTE_IN_SECONDS );
	return true;
}

function wpc_prepare_idempotency( $request ) {
	$method = strtoupper( (string) $request->get_method() );
	if ( ! in_array( $method, array( 'POST', 'PATCH', 'DELETE' ), true ) ) {
		return null;
	}

	$key = trim( (string) $request->get_header( 'idempotency-key' ) );
	if ( '' === $key ) {
		return wpc_error( 400, 'badRequest', 'Idempotency-Key header is required for mutating requests.', 'Idempotency-Key' );
	}

	$hash      = hash( 'sha256', $method . '|' . $request->get_route() . '|' . $request->get_body() );
	$cache_key = 'wpc_idem_' . md5( $key );
	$cached    = get_transient( $cache_key );

	if ( is_array( $cached ) ) {
		if ( ( $cached['hash'] ?? '' ) !== $hash ) {
			return wpc_error(
				409,
				'idempotencyConflict',
				'Idempotency key was reused with a different payload.',
				'Idempotency-Key'
			);
		}
		return new WP_REST_Response( $cached['response'] ?? array(), (int) ( $cached['status'] ?? 200 ) );
	}

	return array(
		'cache_key' => $cache_key,
		'hash'      => $hash,
	);
}

function wpc_store_idempotency( $ctx, $response ) {
	if ( ! is_array( $ctx ) || ! ( $response instanceof WP_REST_Response ) ) {
		return;
	}

	set_transient(
		$ctx['cache_key'],
		array(
			'hash'     => $ctx['hash'],
			'status'   => $response->get_status(),
			'response' => $response->get_data(),
		),
		DAY_IN_SECONDS
	);
}

function wpc_allowed_categories() {
	$defaults = array( 'AI', 'Automation', 'English Learning', 'Productivity', 'Tech Notes' );
	$stored   = get_option( WPC_ALLOWED_CATEGORIES_OPTION, $defaults );
	if ( ! is_array( $stored ) ) {
		return $defaults;
	}
	return array_values( array_unique( array_map( 'sanitize_text_field', $stored ) ) );
}

function wpc_log_action( $action, $post_id = 0, $meta = array() ) {
	$log = get_option( WPC_AUDIT_OPTION, array() );
	if ( ! is_array( $log ) ) {
		$log = array();
	}

	$log[] = array(
		'id'        => wp_generate_uuid4(),
		'time'      => gmdate( 'c' ),
		'user_id'   => get_current_user_id(),
		'ip'        => (string) ( $_SERVER['REMOTE_ADDR'] ?? 'unknown' ),
		'action'    => $action,
		'post_id'   => (int) $post_id,
		'meta'      => $meta,
		'requestId' => wpc_request_id(),
	);

	if ( count( $log ) > 500 ) {
		$log = array_slice( $log, -500 );
	}

	update_option( WPC_AUDIT_OPTION, $log, false );
}

function wpc_map_post( $post ) {
	return array(
		'id'      => (int) $post->ID,
		'title'   => get_the_title( $post->ID ),
		'status'  => $post->post_status,
		'link'    => get_permalink( $post->ID ),
		'date'    => get_post_time( 'c', false, $post, true ),
		'content' => apply_filters( 'the_content', $post->post_content ),
		'excerpt' => $post->post_excerpt,
	);
}

function wpc_ensure_allowed_categories( $names ) {
	if ( ! is_array( $names ) ) {
		return array();
	}

	$allowed = wpc_allowed_categories();
	$term_ids = array();

	foreach ( $names as $name ) {
		$clean = sanitize_text_field( $name );
		if ( '' === $clean ) {
			continue;
		}

		if ( ! in_array( $clean, $allowed, true ) ) {
			return wpc_error( 422, 'unprocessableEntity', 'Category is not in allowed list.', 'categories', array( 'category' => $clean ) );
		}

		$term = get_term_by( 'name', $clean, 'category' );
		if ( ! $term ) {
			$created = wp_insert_term( $clean, 'category' );
			if ( is_wp_error( $created ) ) {
				return wpc_error( 500, 'internalServerError', 'Failed to create category.', 'categories' );
			}
			$term_ids[] = (int) $created['term_id'];
		} else {
			$term_ids[] = (int) $term->term_id;
		}
	}

	return $term_ids;
}

function wpc_health( $request ) {
	return wpc_success(
		array(
			'status'    => 'ok',
			'service'   => 'wordpress-control',
			'timestamp' => gmdate( 'c' ),
		)
	);
}

function wpc_info( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	return wpc_success(
		array(
			'site_name'          => get_bloginfo( 'name' ),
			'site_url'           => get_bloginfo( 'url' ),
			'wp_version'         => get_bloginfo( 'version' ),
			'plugin_version'     => WPC_VERSION,
			'allowed_categories' => wpc_allowed_categories(),
			'capabilities'       => array(
				'explicit_publish' => true,
				'idempotency'      => true,
				'audit_log'        => true,
			),
		)
	);
}

function wpc_list_posts( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$page     = max( 1, (int) $request->get_param( 'page' ) );
	$per_page = min( 100, max( 1, (int) $request->get_param( 'per_page' ) ) );
	$status   = sanitize_text_field( (string) $request->get_param( 'status' ) );
	$search   = sanitize_text_field( (string) $request->get_param( 'search' ) );

	$post_status = array( 'draft', 'future', 'publish' );
	if ( '' !== $status ) {
		$post_status = array_filter( array_map( 'trim', explode( ',', $status ) ) );
	}

	$query = new WP_Query(
		array(
			'post_type'      => 'post',
			'post_status'    => $post_status,
			'posts_per_page' => $per_page,
			'paged'          => $page,
			's'              => $search,
			'orderby'        => 'date',
			'order'          => 'DESC',
		)
	);

	$items = array();
	foreach ( $query->posts as $post ) {
		$items[] = wpc_map_post( $post );
	}

	return wpc_success(
		array(
			'value'      => $items,
			'pagination' => array(
				'page'        => $page,
				'per_page'    => $per_page,
				'total_count' => (int) $query->found_posts,
				'total_pages' => (int) $query->max_num_pages,
			),
		)
	);
}

function wpc_get_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$id   = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	return wpc_success( array( 'post' => wpc_map_post( $post ) ) );
}

function wpc_create_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$body    = (array) $request->get_json_params();
	$title   = sanitize_text_field( (string) ( $body['title'] ?? '' ) );
	$content = wp_kses_post( (string) ( $body['content'] ?? '' ) );
	$status  = sanitize_key( (string) ( $body['status'] ?? 'draft' ) );

	if ( '' === $title ) {
		return wpc_error( 422, 'unprocessableEntity', 'Title is required.', 'title' );
	}

	if ( ! in_array( $status, array( 'draft', 'future', 'private' ), true ) ) {
		return wpc_error( 422, 'unprocessableEntity', 'Unsupported status for create.', 'status' );
	}

	$date_input = (string) ( $body['date'] ?? '' );
	$post_date  = null;
	$post_date_gmt = null;

	if ( 'future' === $status ) {
		$timestamp = strtotime( $date_input );
		if ( ! $timestamp || $timestamp <= time() ) {
			return wpc_error( 422, 'unprocessableEntity', 'Scheduled date must be in the future.', 'date' );
		}
		$post_date     = wp_date( 'Y-m-d H:i:s', $timestamp, wp_timezone() );
		$post_date_gmt = gmdate( 'Y-m-d H:i:s', $timestamp );
	}

	$insert = array(
		'post_type'    => 'post',
		'post_title'   => $title,
		'post_content' => $content,
		'post_status'  => $status,
		'post_excerpt' => sanitize_text_field( (string) ( $body['excerpt'] ?? '' ) ),
	);

	if ( $post_date ) {
		$insert['post_date']     = $post_date;
		$insert['post_date_gmt'] = $post_date_gmt;
	}

	$category_result = wpc_ensure_allowed_categories( $body['categories'] ?? array() );
	if ( $category_result instanceof WP_REST_Response ) {
		return $category_result;
	}
	if ( ! empty( $category_result ) ) {
		$insert['post_category'] = $category_result;
	}

	$post_id = wp_insert_post( $insert, true );
	if ( is_wp_error( $post_id ) ) {
		return wpc_error( 500, 'internalServerError', $post_id->get_error_message(), 'post' );
	}

	if ( isset( $body['seo_title'] ) ) {
		update_post_meta( $post_id, '_yoast_wpseo_title', sanitize_text_field( (string) $body['seo_title'] ) );
	}
	if ( isset( $body['meta_desc'] ) ) {
		update_post_meta( $post_id, '_yoast_wpseo_metadesc', sanitize_text_field( (string) $body['meta_desc'] ) );
	}
	if ( isset( $body['focus_keyword'] ) ) {
		update_post_meta( $post_id, '_yoast_wpseo_focuskw', sanitize_text_field( (string) $body['focus_keyword'] ) );
	}

	wpc_log_action( 'post.create', $post_id, array( 'status' => $status ) );

	$response = wpc_success(
		array(
			'post' => wpc_map_post( get_post( $post_id ) ),
		),
		201
	);
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_patch_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$id   = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	$body = (array) $request->get_json_params();
	if ( isset( $body['status'] ) && 'publish' === sanitize_key( (string) $body['status'] ) ) {
		return wpc_error( 403, 'forbidden', 'Direct publish is blocked. Use /posts/{id}/publish.', 'status' );
	}

	$update = array( 'ID' => $id );

	if ( isset( $body['title'] ) ) {
		$update['post_title'] = sanitize_text_field( (string) $body['title'] );
	}
	if ( isset( $body['content'] ) ) {
		$update['post_content'] = wp_kses_post( (string) $body['content'] );
	}
	if ( isset( $body['excerpt'] ) ) {
		$update['post_excerpt'] = sanitize_text_field( (string) $body['excerpt'] );
	}

	if ( count( $update ) > 1 ) {
		$updated = wp_update_post( $update, true );
		if ( is_wp_error( $updated ) ) {
			return wpc_error( 500, 'internalServerError', $updated->get_error_message(), 'post' );
		}
	}

	if ( isset( $body['seo_title'] ) ) {
		update_post_meta( $id, '_yoast_wpseo_title', sanitize_text_field( (string) $body['seo_title'] ) );
	}
	if ( isset( $body['meta_desc'] ) ) {
		update_post_meta( $id, '_yoast_wpseo_metadesc', sanitize_text_field( (string) $body['meta_desc'] ) );
	}
	if ( isset( $body['focus_keyword'] ) ) {
		update_post_meta( $id, '_yoast_wpseo_focuskw', sanitize_text_field( (string) $body['focus_keyword'] ) );
	}

	wpc_log_action( 'post.patch', $id );

	$response = wpc_success( array( 'post' => wpc_map_post( get_post( $id ) ) ) );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_delete_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$id    = (int) $request->get_param( 'id' );
	$force = rest_sanitize_boolean( $request->get_param( 'force' ) );
	$post  = get_post( $id );

	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	$deleted = wp_delete_post( $id, $force );
	if ( ! $deleted ) {
		return wpc_error( 500, 'internalServerError', 'Failed to delete post.', 'id' );
	}

	wpc_log_action( 'post.delete', $id, array( 'force' => (bool) $force ) );

	$response = wpc_success( array( 'deleted' => true, 'id' => $id ) );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_publish_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$id   = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	$updated = wp_update_post(
		array(
			'ID'          => $id,
			'post_status' => 'publish',
		),
		true
	);

	if ( is_wp_error( $updated ) ) {
		return wpc_error( 500, 'internalServerError', $updated->get_error_message(), 'post' );
	}

	wpc_log_action( 'post.publish', $id );

	$response = wpc_success( array( 'post' => wpc_map_post( get_post( $id ) ) ) );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_schedule_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$id   = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	$body = (array) $request->get_json_params();
	$date = sanitize_text_field( (string) ( $body['date'] ?? '' ) );
	$ts   = strtotime( $date );

	if ( ! $ts || $ts <= time() ) {
		return wpc_error( 422, 'unprocessableEntity', 'Scheduled date must be in the future.', 'date' );
	}

	$updated = wp_update_post(
		array(
			'ID'            => $id,
			'post_status'   => 'future',
			'post_date'     => wp_date( 'Y-m-d H:i:s', $ts, wp_timezone() ),
			'post_date_gmt' => gmdate( 'Y-m-d H:i:s', $ts ),
		),
		true
	);

	if ( is_wp_error( $updated ) ) {
		return wpc_error( 500, 'internalServerError', $updated->get_error_message(), 'post' );
	}

	wpc_log_action( 'post.schedule', $id, array( 'date' => gmdate( 'c', $ts ) ) );

	$response = wpc_success( array( 'post' => wpc_map_post( get_post( $id ) ) ) );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_unschedule_post( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$id   = (int) $request->get_param( 'id' );
	$post = get_post( $id );
	if ( ! $post || 'post' !== $post->post_type ) {
		return wpc_error( 404, 'notFound', 'Post not found.', 'id' );
	}

	$updated = wp_update_post(
		array(
			'ID'          => $id,
			'post_status' => 'draft',
		),
		true
	);

	if ( is_wp_error( $updated ) ) {
		return wpc_error( 500, 'internalServerError', $updated->get_error_message(), 'post' );
	}

	wpc_log_action( 'post.unschedule', $id );

	$response = wpc_success( array( 'post' => wpc_map_post( get_post( $id ) ) ) );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_bulk_create_posts( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$body  = (array) $request->get_json_params();
	$items = $body['posts'] ?? array();
	if ( ! is_array( $items ) || empty( $items ) ) {
		return wpc_error( 422, 'unprocessableEntity', 'posts[] is required for bulk create.', 'posts' );
	}

	$created_ids = array();
	$results     = array();

	foreach ( $items as $idx => $item ) {
		$title = sanitize_text_field( (string) ( $item['title'] ?? '' ) );
		if ( '' === $title ) {
			foreach ( $created_ids as $id ) {
				wp_delete_post( $id, true );
			}
			return wpc_error( 422, 'unprocessableEntity', 'Bulk create failed, rolled back.', 'posts', array( 'index' => $idx ) );
		}

		$post_id = wp_insert_post(
			array(
				'post_type'    => 'post',
				'post_title'   => $title,
				'post_content' => wp_kses_post( (string) ( $item['content'] ?? '' ) ),
				'post_status'  => 'draft',
			),
			true
		);

		if ( is_wp_error( $post_id ) ) {
			foreach ( $created_ids as $id ) {
				wp_delete_post( $id, true );
			}
			return wpc_error( 500, 'internalServerError', 'Bulk create failed, rolled back.', 'posts', array( 'index' => $idx ) );
		}

		$created_ids[] = (int) $post_id;
		$results[]     = wpc_map_post( get_post( $post_id ) );
	}

	wpc_log_action( 'post.bulk_create', 0, array( 'count' => count( $results ) ) );

	$response = wpc_success( array( 'value' => $results ), 201 );
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_list_categories( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$allowed = wpc_allowed_categories();
	$terms   = get_terms(
		array(
			'taxonomy'   => 'category',
			'hide_empty' => false,
		)
	);

	$value = array();
	if ( is_array( $terms ) ) {
		foreach ( $terms as $term ) {
			$value[] = array(
				'id'      => (int) $term->term_id,
				'name'    => $term->name,
				'allowed' => in_array( $term->name, $allowed, true ),
			);
		}
	}

	return wpc_success(
		array(
			'allowed' => $allowed,
			'value'   => $value,
		)
	);
}

function wpc_create_category( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$idempotency = wpc_prepare_idempotency( $request );
	if ( $idempotency instanceof WP_REST_Response ) {
		return $idempotency;
	}

	$body = (array) $request->get_json_params();
	$name = sanitize_text_field( (string) ( $body['name'] ?? '' ) );
	if ( '' === $name ) {
		return wpc_error( 422, 'unprocessableEntity', 'Category name is required.', 'name' );
	}

	$allowed = wpc_allowed_categories();
	if ( ! in_array( $name, $allowed, true ) ) {
		return wpc_error( 422, 'unprocessableEntity', 'Category is not in allowed list.', 'name' );
	}

	$existing = get_term_by( 'name', $name, 'category' );
	if ( $existing ) {
		$response = wpc_success(
			array(
				'category' => array(
					'id'   => (int) $existing->term_id,
					'name' => $existing->name,
				),
			),
			200
		);
		wpc_store_idempotency( $idempotency, $response );
		return $response;
	}

	$created = wp_insert_term( $name, 'category' );
	if ( is_wp_error( $created ) ) {
		return wpc_error( 500, 'internalServerError', $created->get_error_message(), 'name' );
	}

	wpc_log_action( 'category.create', 0, array( 'name' => $name ) );

	$response = wpc_success(
		array(
			'category' => array(
				'id'   => (int) $created['term_id'],
				'name' => $name,
			),
		),
		201
	);
	wpc_store_idempotency( $idempotency, $response );
	return $response;
}

function wpc_get_audit_log( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$log = get_option( WPC_AUDIT_OPTION, array() );
	if ( ! is_array( $log ) ) {
		$log = array();
	}

	return wpc_success( array( 'value' => array_reverse( $log ) ) );
}

function wpc_get_template( $request ) {
	$guard = wpc_guard_private( $request );
	if ( true !== $guard ) {
		return $guard;
	}

	$name = sanitize_key( (string) $request->get_param( 'name' ) );
	$templates = array(
		'how-to' => array(
			'name'        => 'how-to',
			'title_hint'  => 'How to <do something>',
			'structure'   => array( 'intro', 'steps', 'summary' ),
			'word_target' => 900,
		),
		'listicle' => array(
			'name'        => 'listicle',
			'title_hint'  => 'Top N <topic>',
			'structure'   => array( 'intro', 'items', 'closing' ),
			'word_target' => 700,
		),
		'case-study' => array(
			'name'        => 'case-study',
			'title_hint'  => '<problem> to <result>',
			'structure'   => array( 'problem', 'approach', 'result', 'lessons' ),
			'word_target' => 1100,
		),
	);

	if ( ! isset( $templates[ $name ] ) ) {
		return wpc_error( 404, 'notFound', 'Template not found.', 'name' );
	}

	return wpc_success( array( 'template' => $templates[ $name ] ) );
}
