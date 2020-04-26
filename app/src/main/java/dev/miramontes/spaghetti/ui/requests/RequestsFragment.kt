package dev.miramontes.spaghetti.ui.requests

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.Response
import dev.miramontes.spaghetti.R
import dev.miramontes.spaghetti.library.ServerConnection
import dev.miramontes.spaghetti.library.getIdToken

class RequestsFragment : Fragment() {
    private var idToken: String = "NO_TOKEN"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_requests, container, false)
        val inboundView = root.findViewById<RecyclerView>(R.id.inboundView)
        val outboundView = root.findViewById<RecyclerView>(R.id.outboundView)

        activity?.let { activity ->
            getIdToken(activity)?.let { newToken ->
                idToken = newToken
            }
            val serverConnection = ServerConnection(activity, idToken)

            // Create watchable data
            val toUsers = MutableLiveData<MutableList<String>>()
            val toAmounts = MutableLiveData<MutableList<Double>>()
            val toRequestIds = MutableLiveData<MutableList<Long>>()
            val fromUsers = MutableLiveData<MutableList<String>>()
            val fromAmounts = MutableLiveData<MutableList<Double>>()
            val fromRequestIds = MutableLiveData<MutableList<Long>>()

            // Attach adapters
            outboundView.adapter = OutboundRequestsAdapter(
                activity, serverConnection, toUsers, toAmounts, toRequestIds
            )
            outboundView.layoutManager = LinearLayoutManager(context)

            inboundView.adapter = InboundRequestsAdapter(
                activity, serverConnection, fromUsers, fromAmounts, fromRequestIds
            )
            inboundView.layoutManager = LinearLayoutManager(context)

            // Make network requests to update watchable data
            serverConnection.listOutboundRequests(
                Response.Listener { response ->
                    // Split reply into lists
                    val requests = response.getJSONArray("requests")
                    val users = mutableListOf<String>()
                    val amounts = mutableListOf<Double>()
                    val requestIds = mutableListOf<Long>()
                    for (i in 0 until requests.length()) {
                        val request = requests.getJSONArray(i)
                        users.add(request.getString(1))
                        amounts.add(request.getDouble(2))
                        requestIds.add(request.getLong(3))
                    }
                    toUsers.value = users
                    toAmounts.value = amounts
                    toRequestIds.value = requestIds
                    (outboundView.adapter as OutboundRequestsAdapter).notifyDataSetChanged()
                },
                Response.ErrorListener {
                    Log.e("Spaghetti","Failed to Authenticate with the server")
                    activity.finish()
                }
            )
            serverConnection.listInboundRequests(
                Response.Listener { response ->
                    // Split reply into lists
                    val requests = response.getJSONArray("requests")
                    val users = mutableListOf<String>()
                    val amounts = mutableListOf<Double>()
                    val requestIds = mutableListOf<Long>()
                    for (i in 0 until requests.length()) {
                        val request = requests.getJSONArray(i)
                        users.add(request.getString(0))
                        amounts.add(request.getDouble(2))
                        requestIds.add(request.getLong(3))
                    }
                    fromUsers.value = users
                    fromAmounts.value = amounts
                    fromRequestIds.value = requestIds
                    (inboundView.adapter as InboundRequestsAdapter).notifyDataSetChanged()
                },
                Response.ErrorListener {
                    Log.e("Spaghetti","Failed to Authenticate with the server")
                    activity.finish()
                }
            )
        }

        return root
    }
}