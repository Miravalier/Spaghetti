package dev.miramontes.spaghetti.ui.requests

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
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

            // Perform network IO to fill data
            (outboundView.adapter as OutboundRequestsAdapter).NetworkUpdate()
            (inboundView.adapter as InboundRequestsAdapter).NetworkUpdate()
        }

        return root
    }
}