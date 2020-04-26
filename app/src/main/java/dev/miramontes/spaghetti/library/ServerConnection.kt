package dev.miramontes.spaghetti.library

import android.content.Context
import com.android.volley.Request
import com.android.volley.RequestQueue
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONObject

class ServerConnection(private val context: Context, private val idToken: String) {
    private val queue: RequestQueue = Volley.newRequestQueue(context)

    fun status(successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/authstatus",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun netWorth(successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/net-worth",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun listUsers(successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/list-users",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun createTransfer(sourceId: Long, destinationId: Long, amount: Double, successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)
        jsonParameters.put("source", sourceId)
        jsonParameters.put("destination", destinationId)
        jsonParameters.put("amount", amount)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/transfer/create",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun acceptRequest(requestId: Int, successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)
        jsonParameters.put("request", requestId)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/transfer/accept",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun denyRequest(requestId: Int, successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)
        jsonParameters.put("request", requestId)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/transfer/deny",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun listInboundRequests(successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/transfer/list-inbound",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }

    fun listOutboundRequests(successListener: Response.Listener<JSONObject>, errorListener: Response.ErrorListener) {
        // Create json parameters
        val jsonParameters = JSONObject()
        jsonParameters.put("idtoken", idToken)

        // Request a string response from the provided URL.
        val request = JsonObjectRequest(
            Request.Method.PUT,
            "https://spaghetti.miramontes.dev/transfer/list-outbound",
            jsonParameters,
            successListener,
            errorListener
        )

        // Add the request to the RequestQueue.
        queue.add(request)
    }
}